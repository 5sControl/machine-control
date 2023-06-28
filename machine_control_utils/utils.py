import os
import pathlib
import cv2
import logging
import uuid
import requests
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
    import ast
    areas = os.environ.get("extra")

    area_values = []
    if areas:
        areas = ast.literal_eval(areas)
        for dct in areas:
            for coords in dct['coords']:
                x1_area, y1_area, x2_area, y2_area = int(coords['x1']), int(coords['y1']), \
                                                     int(coords['x2']), int(coords['y2'])
                area = Area()
                area.coords = (x1_area, y1_area, x2_area, y2_area)
                area.date = []
                area.imgs = []
                area.zone_name = coords['zoneName']
                area.zone_id = coords['zoneId']
                area_values.append(area)
    else:
        y, x = img_shape[:2]
        area = Area()
        area.coords, area.date, area.imgs = (10, 10, x - 10, y - 10), [], []
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


def get_intersection(box_a, box_b):
    la, ta, ra, ba = box_a
    lb, tb, rb, bb = box_b
    l, t, r, b = max(la, lb), max(ta, tb), min(ra, rb), min(ba, bb)
    return l <= r and t <= b