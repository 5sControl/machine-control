import os
import cv2
import numpy as np
import datetime
from machine_control_utils.HTTPLIB2Capture import HTTPLIB2Capture
from machine_control_utils.utils import (
    send_report_and_save_photo,
    get_intersection,
    get_areas,
)
from machine_control_utils.model import Model


def main(model: Model, img, area_values):
    tracks = model.predict(img)

    for i, a_val in enumerate(area_values):
        x1, y1, x2, y2 = a_val.coords
        huge_box = x1, y1, x2, y2
        huge_box_plot = x1, y1, x2 - x1, y2 - y1

        cv2.putText(
            img,
            str(a_val.zone_id),
            (huge_box_plot[0], huge_box_plot[1] - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (100, 0, 200),
            1,
            cv2.LINE_AA,
        )

        in_area = False
        for track in tracks:
            if not track.is_confirmed():
                continue
            x1, y1, x2, y2 = map(lambda x: int(x), track.to_ltrb())
            small_box = x1, y1, x2, y2
            small_box_plot = x1, y1, x2 - x1, y2 - y1

            cv2.rectangle(img, small_box_plot, (255, 0, 0), 1)  # blue

            if get_intersection(small_box, huge_box):
                in_area = True
                if len(area_values[i].imgs) == 0 or len(area_values[i].imgs) == 3:
                    area_values[i].imgs.append(img)
                    area_values[i].date.append(datetime.datetime.now())
                elif len(area_values[i].imgs) == 1:
                    area_values[i].imgs[0] = img
                    area_values[i].date[0] = datetime.datetime.now()

        if in_area:
            cv2.rectangle(img, huge_box_plot, (0, 200, 0), 2)  # green area
        else:
            cv2.rectangle(img, huge_box_plot, (0, 0, 200), 2)  # red area
            if len(area_values[i].imgs) == 1:
                area_values[i].imgs.append(img)
                area_values[i].date.append(datetime.datetime.now())
                area_values[i].imgs.append(img)
                area_values[i].date.append(datetime.datetime.now())
            if len(area_values[i].imgs) == 3:
                area_values[i].imgs[2] = img
                area_values[i].date[2] = datetime.datetime.now()

    for i, _ in enumerate(area_values):
        print(i, " - ", len(area_values[i].imgs))
        if len(area_values[i].imgs) >= 4:
            send_report_and_save_photo(area_values[i])
            area_values[i].imgs = []
            area_values[i].date = []

    cv2.imshow("img", img)


def run_local(model: Model):
    cap = cv2.VideoCapture(0)
    succes, img = cap.read()
    area_values = get_areas(img.shape)
    while True:
        succes, img = cap.read()
        if succes:
            main(model, img, area_values)
        if cv2.waitKey(1) & 0xFF == 27:
            break
    cap.release()
    cv2.destroyAllWindows()


def run_camera(model):
    username = os.environ.get("username")
    password = os.environ.get("password")
    source = os.environ.get("camera_url")

    dataset = HTTPLIB2Capture(source, username=username, password=password)

    img = dataset.get_snapshot()
    area_values = get_areas(img.shape)

    imgs = [None] * 10
    itr = 0
    while True:
        print(itr)
        img = dataset.get_snapshot()
        imgs[itr] = img
        itr += 1
        if itr >= 10:
            itr = 0
            for img in imgs:
                main(model, img, area_values)
            imgs = [None] * 10
        if cv2.waitKey(1) & 0xFF == 27:
            break
    cv2.destroyAllWindows()


def run_example(model: Model):
    with open("test_image.jpg", "rb") as image:
        f = image.read()
        image = np.asarray(bytearray(f))
        img = cv2.imdecode(image, cv2.IMREAD_COLOR)
    area_values = get_areas(img.shape)
    main(model, img, area_values)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
