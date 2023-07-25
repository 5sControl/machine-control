import pathlib
import cv2
import logging
import uuid
import requests
import colorlog
import ast
import numpy as np
from datetime import datetime
from logging import Logger


class Area:
    def __init__(self, coords):
        x1_area, y1_area, x2_area, y2_area = int(coords['x1']), int(coords['y1']), \
                                             int(coords['x2']), int(coords['y2'])
        self.imgs = []
        self.date = []
        self.coords = (x1_area, y1_area, x2_area, y2_area)
        self.zone_name = coords["zoneName"]
        self.zone_id = coords["zoneId"]

    def __len__(self):
        return len(self.imgs)

    def refresh(self):
        self.imgs = []
        self.date = []

    def update(self, img, idx=None):
        if idx is not None:
            self.imgs[idx] = img
            self.date[idx] = datetime.now()
        else:
            self.imgs.append(img)
            self.date.append(datetime.now())


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
        "algorithm": "machine_control",
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


def get_areas(img_shape: set, extra_data):
    def process_area(coords: dict):
        area = Area(coords)
        areas_data.append(area)

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
            "%(log_color)s%(asctime)s %(levelname)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "CRITICAL": "bold_red,bg_white",
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


def predict_human(img, server_url: str, logger: Logger):
    PORT = 5000
    while True:
        try:
            response = requests.post(
                f"{server_url}:{PORT}/predict_human",
                json={
                    "image": img.tolist()
                }
            )
            break
        except Exception as exc:
            logger.critical(
                "Cannot send request. Error - {}".format(exc)
            )
            continue
    status_code = response.status_code
    if status_code == 200:
        n_boxes = response.json().get('n_boxes')
        coordinates = np.array(response.json().get("coordinates"))
    else:
        logger.warning(
            "Response code = {}.\n response = {}".format(status_code, response)
        )
        n_boxes = None
        coordinates = None
    return [n_boxes, coordinates]
