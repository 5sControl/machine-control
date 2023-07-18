import numpy as np
from yolo_utils.openvino_functional import detect
from openvino.runtime import Core


class YoloDetector:
    def __init__(self, model_path: str, person_conf: float, n_images: int):
        self.model = self.init_model(model_path)
        self.person_conf = person_conf
        self.n_images = n_images

    @staticmethod
    def init_model(model_path):
        core = Core()
        read_model = core.read_model(model_path)
        model = core.compile_model(read_model)
        return model

    def predict(self, img):
        res = detect(np.array(img), self.model)[0]["det"]
        boxes, confs = [], []
        if len(res):
            xyxy = res[:, :4].numpy().astype(np.uint16)
            confs = res[:, 4].numpy()
            classes = res[:, 5].numpy().astype(np.uint8)

            classes_mask = np.where(classes == 0.0)
            conf_mask = np.where(confs > self.person_conf)
            mask = np.intersect1d(classes_mask, conf_mask)

            boxes = xyxy[mask]
            confs = confs[mask]
        return boxes, confs
