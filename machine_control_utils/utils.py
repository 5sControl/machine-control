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
        save_photo_url = f'{folder}/' + str(uuid.uuid4()) + '.jpg'
        photos.append({"image": save_photo_url, "date": str(date)})
        cv2.imwrite(save_photo_url, img)

    logging.debug('photo saved')
    start_tracking = str(area.date[0])
    stop_tracking = str(area.date[-1])

    report_for_send = {
        'camera': folder.split('/')[1],
        'algorithm': 'machine_control',
        'start_tracking': start_tracking,
        'stop_tracking': stop_tracking,
        'photos': photos,
        'violation_found': True,
        'extra': {'zoneId': area.zone_id, 'zoneName': area.zone_name}
    }
    print(report_for_send)
    try:
        requests.post(url=f'{server_url}:80/api/reports/report-with-photos/', json=report_for_send)
    except Exception as exc:
        logging.error('send report:\n' + str(exc))



def get_areas(img_shape):
    areas = os.environ.get("extra")
    logging.debug(areas)

    area_values = []
    areas = ast.literal_eval(areas)
    for dct in areas:
        for coords in dct['coords']:
            area = Area()
            area.coords = (int(coords['x1']), int(coords['y1']), int(coords['x2']), int(coords['y2']))
            area.date, area.imgs = [], []
            area.zone_name = coords['zoneName']
            area.zone_id = coords['zoneId']
            area_values.append(area)
    return area_values


def create_logger():
    logger = logging.getLogger('min_max_logger')
    handler = colorlog.StreamHandler()
    handler.setFormatter(colorlog.ColoredFormatter(
        '%(log_color)s%(asctime)s %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'CRITICAL': 'bold_red,bg_white',
        }))
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    return logger



def calculate_intersection(img, small_box, huge_box):
    # Calculate the coordinates of the intersection rectangle
    x1 = max(small_box[0], huge_box[0])
    y1 = max(small_box[1], huge_box[1])
    x2 = min(small_box[2], huge_box[2])
    y2 = min(small_box[3], huge_box[3])

    # Calculate the areas of the two bounding boxes
    small_box_area = (small_box[2] - small_box[0]) * (small_box[3] - small_box[1])
    # Calculate the area of intersection
    intersection_area = (x2 - x1) * (y2 - y1)

    cv2.rectangle(img, (x1, y1), (x2, y2), (123, 123, 123), 2) # red area

    return intersection_area / float(small_box_area)

