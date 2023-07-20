import abc
from typing import Union
import numpy as np
from yolo_utils.openvino_functional import detect
from openvino.runtime import Core


class ObjectDetectionModel(abc.ABC):
    def __init__(self, model_path: str, person_conf: float):
        self.model = None
        self.model_path = model_path
        self.person_conf = person_conf

    @abc.abstractmethod
    def predict(self, img):
        raise NotImplementedError


class YoloDetector(ObjectDetectionModel):
    def __init__(self, model_path: str, person_conf: float):
        super().__init__(model_path, person_conf)
        self.init_model(model_path)

    def init_model(self, model_path) -> None:
        core = Core()
        read_model = core.read_model(model_path)
        self.model = core.compile_model(read_model)

    def predict(self, img) -> tuple[Union[np.array, list], Union[np.array, list]]:
        res = detect(np.array(img), self.model)[0]["det"]
        boxes, confidence = [], []
        if len(res):
            xyxy = res[:, :4].numpy().astype(np.uint16)
            confidence = res[:, 4].numpy()
            classes = res[:, 5].numpy().astype(np.uint8)

            classes_mask = np.where(classes == 0.0)
            conf_mask = np.where(confidence > self.person_conf)
            mask = np.intersect1d(classes_mask, conf_mask)

            boxes = xyxy[mask]
            confidence = confidence[mask]
        return boxes, confidence
