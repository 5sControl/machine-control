
import os
import uuid
import pathlib
import logging

import cv2
import requests
import httplib2
import numpy as np

from openvino.runtime import Core
from openvino_functional import *


class Area:
    coords = []
    date = []
    imgs = []
    zone_name = None
    zone_id = None


# {
#   "camera_url": "rtsp://192.168.1.167/h264_stream",
#   "algorithm": "machine_control",
#   "server_url": "http://192.168.1.110",
#   "extra": [
#     {
#       "coords": [{
#         "x1": 123,
#         "x2": 232,
#         "y1": 213,
#         "y2": 232,
#         "zoneName": "zone 51",
#         "zoneId": 51
#       }]
#     },
#     {
#       "coords": [{
#         "x1": 123,
#         "x2": 232,
#         "y1": 213,
#         "y2": 232,
#         "zoneName": "zone 52",
#         "zoneId": 52
#       }]
#     }
#   ]
# }


def get_areas(img_shape):
    import ast
    areas = os.environ.get("extra")
    print(areas)

    area_values = []
    if areas:
        areas = ast.literal_eval(areas)
        for dct in areas:
            for coords in dct['coords']:
                x1_area, y1_area, x2_area, y2_area = int(coords['x1']), int(coords['y1']), int(coords['x2']), int(coords['y2'])
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


def init_connection():
    password =  os.environ.get("password")
    username =  os.environ.get("username")
    try:
        h = httplib2.Http(".cache")
        h.add_credentials(username, password)
        return h
    except Exception as exc:
        logging.error('init connection:\n' + str(exc))
    return None


def init_model():
    core = Core()
    read_model = core.read_model('yolov8m_openvino_model/yolov8m.xml')
    model = core.compile_model(read_model, "CPU")
    return model


def get_frame(h):
    try:
        _, content = h.request(os.environ.get("camera_url"), "GET", body="foobar")
        nparr = np.frombuffer(content, np.uint8)
        img0 = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return img0
    except Exception as exc:
        logging.error('get frame:\n' + str(exc))
    return None

def predict(model, img):
    CONF = 0.4
    res = detect(np.array(img), model)[0]['det']
    if len(res):
        xyxy, confs, classes  = res[:, :4].numpy().astype(np.uint16), res[:, 4].numpy(), res[:, 5].numpy().astype(np.uint8)
        classes_mask, = np.where(classes == 0.)
        conf_mask, = np.where(confs > CONF)
        
        mask = np.intersect1d(classes_mask, conf_mask)

        boxes = xyxy[mask] if len(mask) else []
        confs = confs[mask] if len(mask) else []
        
        return boxes, confs
    return [], []


def put_rectangle(img, boxes, scores):
    for (x1, y1, x2, y2), score in zip(boxes, scores):
        cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), 2)
        cv2.putText(img, str(score), (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
    return img


def send_report_and_save_photo(area):
    server_url =  os.environ.get("server_url")
    folder =  os.environ.get("folder")

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
    