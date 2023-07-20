import os
import cv2
from typing import List
from machine_control_utils.HTTPLIB2Capture import HTTPLIB2Capture
from logging import Logger
from machine_control_utils.utils import (
    Area,
    predict_human,
    send_report_and_save_photo,
    get_intersection,
    get_areas,
)

GREEN = (0, 200, 0)
RED = (0, 0, 200)
BLUE = (255, 0, 0)


def run_machine_control(img, areas_data: List[Area], logger: Logger) -> None:
    boxes, confidence = predict_human(img, server_url, logger)

    for i, a_val in enumerate(areas_data):
        x1, y1, x2, y2 = a_val.coords
        area_box = x1, y1, x2, y2
        area_box_plot = x1, y1, x2 - x1, y2 - y1

        cv2.putText(img, str(a_val.zone_id), (area_box_plot[0], area_box_plot[1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 0, 200), 1, cv2.LINE_AA)

        in_area = False
        for (x1, y1, x2, y2), conf in zip(boxes, confidence):
            human_box = x1, y1, x2, y2
            human_box_plot = x1, y1, x2 - x1, y2 - y1

            cv2.rectangle(img, human_box_plot, BLUE, 1)

            if get_intersection(human_box, area_box, threshold=0.25):
                in_area = True

        areas_data[i].capture_update(img, in_area=in_area)

        color = GREEN if in_area else RED
        cv2.rectangle(img, area_box_plot, color, 2)

    for i, _ in enumerate(areas_data):
        if len(areas_data[i]) >= 4:
            send_report_and_save_photo(areas_data[i])
            areas_data[i].refresh()


def run_camera() -> None:
    username = os.environ.get("username")
    password = os.environ.get("password")
    source = os.environ.get("camera_url")

    dataset = HTTPLIB2Capture(source, username=username, password=password)

    img = dataset.get_snapshots()[0]
    areas_data = get_areas(img.shape)

    while True:
        imgs = dataset.get_snapshots()
        for img in imgs:
            run_machine_control(img, areas_data)


def run_local() -> None:
    cap = cv2.VideoCapture(1)
    succes, img = cap.read()
    areas_data = get_areas(img.shape)

    while True:
        succes, img = cap.read()
        if succes:
            run_machine_control(img, areas_data)
            cv2.imshow("img", img)
        if cv2.waitKey(1) & 0xFF == 27:
            break
        cv2.imshow("img", img)

    cap.release()
    cv2.destroyAllWindows()


def run_example() -> None:
    img = cv2.imread("test_image.jpg")
    areas_data = get_areas(img.shape)
    run_machine_control(img, areas_data)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
