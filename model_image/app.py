from ObjectDetectionModel import YoloDetector
from flask_config.load_config import *
import logging
import colorlog
import numpy as np
from PIL import Image
import io
import ray
from flask import Flask, request, jsonify


logger = logging.getLogger('machine_control_logger')
handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
        "%(log_color)s[%(asctime)s][%(levelname)s] - %(message)s",
        datefmt='%Y-%m-%d %H:%M:%S',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'CRITICAL': 'bold_red,bg_white',
        }))
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)
logger.propagate = False


@ray.remote
class MyModel:
    def __init__(self):
        self.model = YoloDetector(MODEL_PATH, PERSOR_CONF)
        self.convert_bytes2image = lambda bytes: np.array(Image.open(io.BytesIO(bytes)), dtype=np.uint8)

    def process_request(self, data):
        data = self.convert_bytes2image(data)
        boxes, confidence = self.model.predict(data)
        return boxes, confidence


app = Flask(__name__)
ray.init(num_cpus=8)
model = MyModel.remote()


@app.route('/predict_human', methods=['POST'])
def process():
    if request.method == "POST":
        data = request.files["img"].read()
        result = model.process_request.remote(data)
        boxes, confidence = ray.get(result)
        logger.info("Request to predict_human: Success")
        return jsonify(
            {
                "boxes": boxes.tolist(),
                "confidence": confidence.tolist()
            }
        )
