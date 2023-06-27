import os
import pathlib
import cv2
import logging
import uuid
import requests
import ast
import colorlog


class Area:
    date = []
    imgs = []
    coords = []
    zone_name = None
    zone_id = None


def send_report_and_save_photo(area):
    server_url = os.environ.get("server_url")
    folder = os.environ.get("folder")

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


def get_areas(img_shape):
    areas = os.environ.get("extra")
    logging.debug(areas)

    area_values = []
    areas = ast.literal_eval(areas)
    for dct in areas:
        for coords in dct["coords"]:
            area = Area()
            area.coords = (
                int(coords["x1"]),
                int(coords["y1"]),
                int(coords["x2"]),
                int(coords["y2"]),
            )
            area.date, area.imgs = [], []
            area.zone_name = coords["zoneName"]
            area.zone_id = coords["zoneId"]
            area_values.append(area)
    return area_values


def create_logger():
    logger = logging.getLogger("min_max_logger")
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


def get_intersection(box1, box2):
    # Ensure the input boxes are in the format [x_min, y_min, x_max, y_max]
    assert len(box1) == 4, "Box1 should contain 4 values: [x_min, y_min, x_max, y_max]"
    assert len(box2) == 4, "Box2 should contain 4 values: [x_min, y_min, x_max, y_max]"

    # Order the coordinates (x_min, y_min, x_max, y_max)
    x_min1, y_min1, x_max1, y_max1 = (
        min(box1[0], box1[2]),
        min(box1[1], box1[3]),
        max(box1[0], box1[2]),
        max(box1[1], box1[3]),
    )
    x_min2, y_min2, x_max2, y_max2 = (
        min(box2[0], box2[2]),
        min(box2[1], box2[3]),
        max(box2[0], box2[2]),
        max(box2[1], box2[3]),
    )

    x_min = max(x_min1, x_min2)
    y_min = max(y_min1, y_min2)
    x_max = min(x_max1, x_max2)
    y_max = min(y_max1, y_max2)

    intersection_area = max(0, x_max - x_min + 1) * max(0, y_max - y_min + 1)
    if intersection_area <= 0:
        return False
    else:
        return True
