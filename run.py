import os
import cv2
from typing import List
from machine_control_utils.HTTPLIB2Capture import HTTPLIB2Capture
from machine_control_utils.model import YoloDetector
from machine_control_utils.utils import (
    send_report_and_save_photo,
    get_intersection,
    get_areas,
    Area,
)
from datetime import datetime, timedelta


GREEN = (0, 200, 0)
RED = (0, 0, 200)
BLUE = (255, 0, 0)


def run_machine_control(model: YoloDetector, img, areas_data: List[Area]):
    boxes, confs = model.predict(img)

    for i, a_val in enumerate(areas_data):
        x1, y1, x2, y2 = a_val.coords
        area_box = x1, y1, x2, y2
        area_box_plot = x1, y1, x2 - x1, y2 - y1

        cv2.putText(img, str(a_val.zone_id), (area_box_plot[0], area_box_plot[1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 0, 200), 1, cv2.LINE_AA)

        in_area = False
        for (x1, y1, x2, y2), conf in zip(boxes, confs):
            human_box = x1, y1, x2, y2
            human_box_plot = x1, y1, x2 - x1, y2 - y1

            cv2.rectangle(img, human_box_plot, BLUE, 1)

            if get_intersection(human_box, area_box, threshold=0.25):
                in_area = True
                if len(areas_data[i]) == 0:
                    areas_data[i].update(img)
                elif len(areas_data[i]) == 1:
                    areas_data[i].update(img, idx=0)
                elif len(areas_data[i]) == 3:
                    if datetime.now() - areas_data[i].date[0] > timedelta(minutes=30):
                        areas_data[i].refresh()
                    areas_data[i].update(img)

        if not in_area:
            if len(areas_data[i]) == 1:
                areas_data[i].update(img)
                areas_data[i].update(img)
            if len(areas_data[i]) == 3:
                areas_data[i].update(img, idx=2)

        color = GREEN if in_area else RED
        cv2.rectangle(img, area_box_plot, color, 2)

    for i, _ in enumerate(areas_data):
        if len(areas_data[i]) >= 4:
            send_report_and_save_photo(areas_data[i])
            areas_data[i].refresh()


def run_local(model: YoloDetector):
    cap = cv2.VideoCapture(1)
    succes, img = cap.read()
    areas_data = get_areas(img.shape)

    while True:
        succes, img = cap.read()
        if succes:
            run_machine_control(model, img, areas_data)
            cv2.imshow("img", img)
        if cv2.waitKey(1) & 0xFF == 27:
            break
        cv2.imshow("img", img)

    cap.release()
    cv2.destroyAllWindows()


def run_camera(model: YoloDetector):
    username = os.environ.get("username")
    password = os.environ.get("password")
    source = os.environ.get("camera_url")

    dataset = HTTPLIB2Capture(source, username=username, password=password)

    img = dataset.get_snapshots()[0]
    areas_data = get_areas(img.shape)

    while True:
        imgs = dataset.get_snapshots(n_images=model.n_images)
        for img in imgs:
            run_machine_control(model, img, areas_data)


def run_example(model: YoloDetector):
    img = cv2.imread("test_image.jpg")
    areas_data = get_areas(img.shape)
    run_machine_control(model, img, areas_data)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
