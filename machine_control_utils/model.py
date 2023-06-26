import numpy as np
from yolo_utils.openvino_functional import detect
from openvino.runtime import Core
from deep_sort_realtime.deepsort_tracker import DeepSort


class Model:
    def __init__(
            self,
            object_detector_path: str,
            person_conf: float,
            person_in_frame: float
            ):
        self.person_in_frame = person_in_frame
        self.object_detector = YoloDetector(object_detector_path, person_conf)
        self.object_tracker = DeepSort(
            max_age=3,
            # n_init=2,
            # nms_max_overlap=1.0,
            # max_cosine_distance=0.5,
            # nn_budget=None,
            # override_track_class=None,
            # embedder="mobilenet",
            ) 
        
    
    def predict(self, img):
        boxes, confs = self.object_detector.predict_boxes(img)
        detections: list = []
        for (x1, y1, x2, y2), conf in zip(boxes, confs):
            detections.append(((x1, y1, x2 - x1, y2 - y1), conf, 'person'))
        tracks = self.object_tracker.update_tracks(detections, frame=img)
        return tracks


class YoloDetector(Model):
    def __init__(
            self, 
            model_path: str, 
            person_conf: float
            ):
        self.model = self.init_model(model_path)
        self.person_conf = person_conf

    @staticmethod
    def init_model(model_path):
        core = Core()
        read_model = core.read_model(model_path)
        model = core.compile_model(read_model)
        return model

    def predict_boxes(self, img):
        res = detect(np.array(img), self.model)[0]['det']
        boxes, confs = [], []
        if len(res):
            xyxy = res[:, :4].numpy().astype(np.uint16)
            confs = res[:, 4].numpy()
            classes = res[:, 5].numpy().astype(np.uint8)

            classes_mask = np.where(classes == 0.)
            conf_mask = np.where(confs > self.person_conf)
            mask = np.intersect1d(classes_mask, conf_mask)
            
            boxes = xyxy[mask]
            confs = confs[mask]
        return boxes, confs
