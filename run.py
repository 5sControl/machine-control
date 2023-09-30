import time

import cv2
from machine_control_utils.HTTPLIB2Capture import HTTPLIB2Capture
from logging import Logger
from machine_control_utils.utils import (
    predict_human,
    send_report_and_save_photo,
    get_areas,
)


GREEN = (0, 200, 0)
RED = (0, 0, 200)
BLUE = (255, 0, 0)
PURPLE = (100, 0, 200)


def run_machine_control(dataset: HTTPLIB2Capture, logger: Logger,
                        extra: str, server_url: str, folder: str) -> None:
    logger.info(f'Input parameters:')
    logger.info(f'{server_url=}')
    logger.info(f'{extra=}')

    areas_data = get_areas(dataset, extra)
    start = end = time.time()
    while True:
        if end - start < 1:
            lag = end - start
            logger.debug(f'Algorithm speed per iteration {lag}')
            logger.debug(f'Sleep time: {1 - lag}')
            time.sleep(1 - lag)
        start = time.time()

        img_clear = dataset.get_snapshot()
        for idx, area in enumerate(areas_data):
            img = img_clear.copy()
            x1, y1, x2, y2 = area.coords
            area_box_plot = x1, y1, x2 - x1, y2 - y1

            cv2.putText(img, str(area.zone_id), (area_box_plot[0], area_box_plot[1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, PURPLE, 1, cv2.LINE_AA)

            boxes, confidence = predict_human(img[y1:y2, x1:x2], server_url, logger)

            in_area = False
            if len(boxes) != 0:
                in_area = True
                for (h_x1, h_y1, h_x2, h_y2), conf in zip(boxes, confidence):
                    h_x1, h_y1, h_x2, h_y2 = h_x1 + x1, h_y1 + y1, h_x2 + x1, h_y2 + y1
                    human_box_plot = h_x1, h_y1, h_x2 - h_x1, h_y2 - h_y1

                    cv2.rectangle(img, human_box_plot, BLUE, 3)
                    cv2.putText(img, str(conf)[:4], (human_box_plot[0], human_box_plot[1] - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, PURPLE, 1, cv2.LINE_AA)

            color = GREEN if in_area else RED
            cv2.rectangle(img, area_box_plot, color, 2)

            areas_data[idx].update(img, in_area)

            if dataset.is_local:
                cv2.imshow("img", img)
                if cv2.waitKey(1) & 0xFF == 27:
                    break

        for idx, _ in enumerate(areas_data):
            if len(areas_data[idx]) >= 4:
                send_report_and_save_photo(areas_data[idx], folder, server_url)
                areas_data[idx].refresh()
        end = time.time()