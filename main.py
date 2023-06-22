import cv2
import torch
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


load_dotenv()


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
    def __init__(self):
        self.model = self.load_model()
        self.classes = self.model.names

    # def load_model(self):
    #     model_path = 'yolov5s.pth'
    #     model_weight_path = 'yolov5s_10cls.pt'
    #
    #     if os.path.isfile(model_path):
    #         model = torch.load(model_path)
    #         ckpt = torch.load(model_weight_path)
    #         model.load_state_dict(ckpt['model'].state_dict())
    #     else:
    #         model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
    #
    #     torch.save(model, model_path)
    #     torch.save(model.state_dict(), model_weight_path)
    #     model.eval()
    #     return model

    def load_model(self):
        model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
        return model

    def score_frame(self, frame):
        downscale_factor = 1
        width = int(frame.shape[1] / downscale_factor)
        height = int(frame.shape[0] / downscale_factor)
        frame = cv2.resize(frame, (width, height))
        results = self.model(frame)
        labels, cord = results.xyxyn[0][:, -1], results.xyxyn[0][:, :-1]
        return labels, cord

    def class_to_label(self, x):
        return self.classes[int(x)]

    def filter_boxes(self, results, frame, height, width, confidence=0.35):
        labels, cord = results
        detections = []
        feature = "person"

        n = len(labels)
        x_shape, y_shape = width, height

        for i in range(n):
            if self.class_to_label(labels[i]) == feature:
                row = cord[i]
                if row[4] >= confidence:
                    x1, y1, x2, y2 = (
                        int(row[0] * x_shape),
                        int(row[1] * y_shape),
                        int(row[2] * x_shape),
                        int(row[3] * y_shape),
                    )
                    confidence = float(row[4].item())
                    detections.append(
                        ([x1, y1, int(x2 - x1), int(y2 - y1)], row[4].item(), feature)
                    )
        return frame, detections


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
    import ast
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
        area = Area()
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
    results = detector.score_frame(img)
    img, detections = detector.filter_boxes(results, img, height=img.shape[0], width=img.shape[1], confidence=0.35)
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
            small_box = list(map(int, track.to_ltrb()))
            x1, y1, x2, y2 = small_box
            cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), 2)  # blue

            if calculate_intersection(small_box, huge_box) > 0.15:
                in_area = True
                # cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), 2) # blue
                if len(area_values[i].imgs) == 0 or len(area_values[i].imgs) == 3:
                    area_values[i].imgs.append(img)
                    area_values[i].date.append(datetime.datetime.now())
                elif len(area_values[i].imgs) == 1:
                    area_values[i].imgs[0] = img
                    area_values[i].date[0] = datetime.datetime.now()

            if in_area:
                # cv2.putText(img, str(conf), (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
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
            # print('BINGOO!!!')
            area_values[i].imgs = []
            area_values[i].date = []

    cv2.imshow("img", img)


def run_local():
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1980)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1200)

    succes, img = cap.read()
    area_values = get_areas(img.shape)

    while True:
        succes, img = cap.read()
        if succes:
            main(img, area_values)

        if cv2.waitKey(1) & 0xFF == 27:
            break
    cap.release()
    cv2.destroyAllWindows()


def rum_camera():
    username = os.environ.get("username")
    password = os.environ.get("password")
    source = os.environ.get("camera_url")

    dataset = HTTPLIB2Capture(source, username=username, password=password)

    img = dataset.get_snapshot()
    area_values = get_areas(img.shape)

    while True:
        img = dataset.get_snapshot()
        if img:
            main(img, area_values)


detector = YoloDetector()
object_tracker = DeepSort(
    max_age=5,
    n_init=3,
    nms_max_overlap=1.0,
    max_cosine_distance=0.3,
    nn_budget=None,
    override_track_class=None,
    embedder="mobilenet",
    half=True,
    bgr=True,
    embedder_gpu=True,
    embedder_model_name=None,
    embedder_wts=None,
    polygon=False,
    today=None,
)


if __name__ == '__main__':
    run_local()
