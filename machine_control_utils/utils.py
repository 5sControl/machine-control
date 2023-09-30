import os
import pathlib
import time
from machine_control_utils.HTTPLIB2Capture import HTTPLIB2Capture
import cv2
import logging
import uuid
import requests
import colorlog
import ast
import numpy as np
from datetime import datetime
from logging import Logger
from PIL import Image
import io


PORT = 5002


class Area:
    def __init__(self, coords):
        x1_area, y1_area, x2_area, y2_area = int(coords['x1']), int(coords['y1']), \
                                             int(coords['x2']), int(coords['y2'])
        self.imgs = []
        self.date = []
        self.coords = (x1_area, y1_area, x2_area, y2_area)
        self.zone_name = coords["zoneName"]
        self.zone_id = coords["zoneId"]

    def __eq__(self, other: str):
        if (len(self) == 0 and other == 'first') or \
           (len(self) == 1 and other == 'second') or \
           (len(self) == 2 and other == 'third') or \
           (len(self) == 3 and other == 'fourth'):
            return True
        else:
            return False

    def __len__(self):
        return len(self.imgs)

    def refresh(self):
        self.imgs = []
        self.date = []

    def update(self, img, in_area: bool):
        if in_area:
            if self == 'first':
                self.imgs.append(img)
                self.date.append(datetime.now())
            elif self == 'second':
                self.imgs[0] = img
                self.date[0] = datetime.now()
            elif self == 'third':
                self.imgs.append(self.imgs[1])
                self.date.append(datetime.now())
                self.imgs.append(img)
                self.date.append(datetime.now())
            elif self == 'fourth':
                self.imgs.append(img)
                self.date.append(datetime.now())
        else:
            if self == 'first':
                pass
            elif self == 'second':
                self.imgs.append(img)
                self.date.append(datetime.now())
            elif self == 'third':
                self.imgs.append(img)
                self.date.append(datetime.now())
            elif self == 'fourth':
                self.imgs[2] = img
                self.date[2] = datetime.now()


def get_areas(dataset: HTTPLIB2Capture, extra_data):
    def process_area(coords: dict):
        area = Area(coords)
        areas_data.append(area)

    img = None
    while img is None:
        img = dataset.get_snapshot()
        time.sleep(1)
    img_shape = img.shape

    areas_data, extra = [], []

    if extra_data:
        extra = ast.literal_eval(extra_data)
    if not extra:
        y, x = img_shape[:2]
        extra = [{"coords": [{"x1": 10, "x2": x - 10, "y1": 10, "y2": y - 10, "zoneName": None, "zoneId": None}]}]
    for dct in extra:
        for coords in dct['coords']:
            process_area(coords)
    return areas_data


def create_logger():
    logger = logging.getLogger("machine_control_logger")
    handler = colorlog.StreamHandler()
    handler.setFormatter(
        colorlog.ColoredFormatter(
            "%(log_color)s[%(asctime)s][%(levelname)s] - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "CRITICAL": "red",
            },
        )
    )
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    return logger


def get_intersection(box_a, box_b, threshold=0.25):
    la, ta, ra, ba = box_a
    lb, tb, rb, bb = box_b
    l, t, r, b = max(la, lb), max(ta, tb), min(ra, rb), min(ba, bb)

    human_area = (ra - la + 1) * (ba - ta + 1)
    box_area = (rb - lb + 1) * (bb - tb + 1)
    intersection_area = max(0, (r - l + 1)) * max(0, (b - t + 1))

    if box_area > human_area:
        intersection_box = intersection_area / human_area
    else:
        intersection_box = intersection_area / box_area
    return intersection_box > threshold


def _convert_image2bytes(image: np.array, format='PNG') -> io.BytesIO:
    pil_image = Image.fromarray(image)
    img_byte_arr = io.BytesIO()
    pil_image.save(img_byte_arr, format=format)
    img_byte_arr.seek(0)
    return img_byte_arr


def predict_human(img, server_url: str, logger: Logger):
    try:
        response = requests.post(
            f"{server_url}:{PORT}/predict_human",
            files={
                "img": _convert_image2bytes(img)
            }
        )
        response.raise_for_status()
        boxes = np.array(response.json().get("boxes"))
        confidence = np.array(response.json().get("confidence"))
    except Exception as exc:
        boxes, confidence = [], []
        logger.critical("Cannot send request. Error - {}".format(exc))
    return boxes, confidence


def send_report_and_save_photo(area, folder: str, server_url: str):
    pathlib.Path(folder).mkdir(exist_ok=True, parents=True)

    photos = []
    for img, date in zip(area.imgs, area.date):
        save_photo_url = f"{folder}/" + str(uuid.uuid4()) + ".jpg"
        photos.append({"image": save_photo_url, "date": str(date)})
        cv2.imwrite(save_photo_url, img)

    logging.debug("photo saved")
    start_tracking = str(area.date[0])
    stop_tracking = str(area.date[-1])

    report_for_send = {
        "camera": folder.split("/")[1],
        "algorithm": os.environ.get("algorithm_name"),
        "start_tracking": start_tracking,
        "stop_tracking": stop_tracking,
        "photos": photos,
        "violation_found": True,
        "extra": {"zoneId": area.zone_id, "zoneName": area.zone_name},
    }
    print(report_for_send)
    try:
        requests.post(
            url=f"{server_url}:80/api/reports/report-with-photos/", json=report_for_send
        )
    except Exception as exc:
        logging.error("send report:\n" + str(exc))
