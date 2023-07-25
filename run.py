import cv2
from machine_control_utils.HTTPLIB2Capture import HTTPLIB2Capture
from logging import Logger
from config.load_config import INTERSECTION_THRESHOLD, TIMEDELTA_MINUTES
from machine_control_utils.utils import (
    predict_human,
    send_report_and_save_photo,
    get_intersection,
    get_areas,
)
from datetime import datetime, timedelta


GREEN = (0, 200, 0)
RED = (0, 0, 200)
BLUE = (255, 0, 0)


def run_machine_control(dataset: HTTPLIB2Capture, logger: Logger,
                        extra: str, server_url: str, folder: str) -> None:
    img = dataset.get_snapshot()
    areas_data = get_areas(img.shape, extra)

    while True:
        img = dataset.get_snapshot()
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

                if get_intersection(human_box, area_box, threshold=INTERSECTION_THRESHOLD):
                    in_area = True
                    if len(areas_data[i]) == 0:
                        areas_data[i].update(img)
                    elif len(areas_data[i]) == 1:
                        areas_data[i].update(img, idx=0)
                    elif len(areas_data[i]) == 3:
                        if datetime.now() - areas_data[i].date[0] > timedelta(minutes=TIMEDELTA_MINUTES):
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
                send_report_and_save_photo(areas_data[i], folder, server_url)
                areas_data[i].refresh()
