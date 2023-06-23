import cv2
from deep_sort_realtime.deepsort_tracker import DeepSort
import httplib2
import numpy as np
import os
import logging
import datetime
from dotenv import load_dotenv
import requests
import pathlib
import uuid
from openvino.runtime import Core
from yolo_utils.openvino_functional import detect
import ast

load_dotenv()

downscale_factor = 1
person_conf = 0.3
person_in_frame = 0.1


class HTTPLIB2Capture:
    def __init__(self, path, **kwargs):
        self.h = httplib2.Http(".cache")
        self.camera_url = path
        self.username = kwargs.get('username', None)
        self.password = kwargs.get('password', None)
        if self.username is None or self.password is None:
            raise Exception

    def get_snapshot(self):
        self.h.add_credentials(self.username, self.password)
        try:
            resp, content = self.h.request(
                self.camera_url, "GET", body="foobar")
            img_array = np.frombuffer(content, np.uint8)
            image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            return image
        except Exception:
            return None


class YoloDetector:
    def __init__(self, model_path):
        self.model = self.init_model(model_path)

    @staticmethod
    def init_model(model_path):
        core = Core()
        read_model = core.read_model(model_path)
        model = core.compile_model(read_model)
        return model

    def predict_filter(self, img):
        res = detect(np.array(img), self.model)[0]['det']
        if len(res):
            xyxy, confs, classes = res[:, :4].numpy().astype(np.uint16), res[:, 4].numpy(), res[:, 5].numpy().astype(
                np.uint8)
            classes_mask, = np.where(classes == 0.)
            conf_mask, = np.where(person_conf)
            mask = np.intersect1d(classes_mask, conf_mask)

            boxes = xyxy[mask] if len(mask) else []
            confs = confs[mask] if len(mask) else []

            return boxes, confs
        return [], []


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


class Area:
    date = []
    imgs = []
    coords = []
    zone_name = None
    zone_id = None


def get_areas(img_shape):
    areas = os.environ.get("extra")
    logging.debug(areas)

    area_values = []
    if areas:
        areas = ast.literal_eval(areas)
        for dct in areas:
            for coords in dct['coords']:
                area = Area()
                area.coords = (int(coords['x1']), int(coords['y1']), int(coords['x2']), int(coords['y2']))
                area.date, area.imgs = [], []
                area.zone_name = coords['zoneName']
                area.zone_id = coords['zoneId']
                area_values.append(area)
    else:
        area = Area() # TODO: delete
        y, x = img_shape[:2]
        area.coords, area.date, area.imgs = (10, 10, x - 10, y - 10), [], []
        area_values.append(area)
    return area_values


def calculate_intersection(small_box, huge_box):
    # Calculate the coordinates of the intersection rectangle
    x1 = max(small_box[0], huge_box[0])
    y1 = max(small_box[1], huge_box[1])
    x2 = min(small_box[2], huge_box[2])
    y2 = min(small_box[3], huge_box[3])

    # Calculate the areas of the two bounding boxes
    small_box_area = (small_box[2] - small_box[0]) * (small_box[3] - small_box[1])
    # Calculate the area of intersection
    intersection_area = (x2 - x1) * (y2 - y1)

    return intersection_area / float(small_box_area)


def main(img, area_values):
    boxes, confs = detector.predict_filter(img)
    detections: list = []
    for (x1, y1, x2, y2), conf in zip(boxes, confs):
        detections.append(
            ((x1, y1, x2 - x1, y2 - y1), conf, 'person')
        )
        cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 255), 2)  # blue
    tracks = object_tracker.update_tracks(detections, frame=img)
    for i, a_val in enumerate(area_values):
        huge_box = a_val.coords
        x1_area, y1_area, x2_area, y2_area = huge_box

        cv2.rectangle(img, (x1_area, y1_area), (x2_area, y2_area), (0, 0, 200), 2)  # red area
        cv2.putText(img, str(a_val.zone_name) + " : " + str(a_val.zone_id), (x1_area, y1_area - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (100, 0, 200), 5, cv2.LINE_AA)

        in_area = False
        for track in tracks:
            if not track.is_confirmed():
                continue
            x1, y1, x2, y2 = list(map(lambda x: int(x * downscale_factor), track.to_ltrb()))
            small_box = x1, y1, x2, y2

            cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), 2)  # blue

            if calculate_intersection(small_box, huge_box) > person_in_frame:
                in_area = True
                # cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), 2) # blue
                if len(area_values[i].imgs) == 0 or len(area_values[i].imgs) == 3:
                    area_values[i].imgs.append(img)
                    area_values[i].date.append(datetime.datetime.now())
                elif len(area_values[i].imgs) == 1:
                    area_values[i].imgs[0] = img
                    area_values[i].date[0] = datetime.datetime.now()

            if in_area:
                cv2.rectangle(img, (x1_area, y1_area), (x2_area, y2_area), (0, 200, 0), 2) # green area
            else:
                if len(area_values[i].imgs) == 1:
                    area_values[i].imgs.append(img)
                    area_values[i].date.append(datetime.datetime.now())
                    area_values[i].imgs.append(img)
                    area_values[i].date.append(datetime.datetime.now())
                if len(area_values[i].imgs) == 3:
                    area_values[i].imgs[2] = img
                    area_values[i].date[2] = datetime.datetime.now()

    for i, _ in enumerate(area_values):
        if i == 1:
            print(len(area_values[i].imgs))
        if len(area_values[i].imgs) >= 4:
            send_report_and_save_photo(area_values[i])
            area_values[i].imgs = []
            area_values[i].date = []

    cv2.imshow("img", img)

def run_local():
    cap = cv2.VideoCapture(0)
    # cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1980)
    # cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1200)

    succes, img = cap.read()
    area_values = get_areas(img.shape)
    imgs: list = []
    while True:
        succes, img = cap.read()
        # while len(imgs) < 10:
        #     succes, img = cap.read()
        #     if succes:
        #         imgs.append(img)
        # for img in imgs:
        main(img, area_values)
        if cv2.waitKey(1) & 0xFF == 27:
            break
    cap.release()
    cv2.destroyAllWindows()


def run_camera():
    username = os.environ.get("username")
    password = os.environ.get("password")
    source = os.environ.get("camera_url")

    dataset = HTTPLIB2Capture(source, username=username, password=password)

    img = dataset.get_snapshot()
    area_values = get_areas(img.shape)
    count = 1
    while True:
        print(count)
        count += 1
        img = dataset.get_snapshot()
        if img is not None:
            main(img, area_values)
        if cv2.waitKey(1) & 0xFF == 27:
            break
    cv2.destroyAllWindows()


detector = YoloDetector(model_path='model/yolov8n.xml')
object_tracker = DeepSort(
    max_age=5,
    # n_init=2,
    # nms_max_overlap=1.0,
    # max_cosine_distance=0.3,
    # nn_budget=None,
    # override_track_class=None,
    # embedder="mobilenet",
    # half=True,
    # bgr=True,
    # embedder_gpu=False,
    # embedder_model_name=None,
    # embedder_wts=None,
    # polygon=False,
    # today=None,
)


if __name__ == '__main__':
    run_local()

# extra=[{"coords": [{"x1": 10, "x2": 1000, "y1": 100, "y2": 1000, "zoneName": "zone 51", "zoneId": 51 }] }, { "coords": [{ "x1": 1050, "x2": 2000, "y1": 0, "y2": 1000, "zoneName": "zone 52", "zoneId": 52 }] } ]
