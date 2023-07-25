from flask import Flask, jsonify, request
from ObjectDetectionModel import YoloDetector
from flask_config.load_config import *
import logging
import colorlog


app = Flask(__name__)
model = YoloDetector(MODEL_PATH, PERSOR_CONF)

logger = logging.getLogger('machine_control_logger')
handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
        '%(log_color)s%(asctime)s %(levelname)s: %(message)s',
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


@app.route('/predict_human', methods=['POST'])
def predict_human():
    if request.method == 'POST':
        img = request.json['img']
        boxes, confidence = model.predict(img)
        logger.info("Request to predict_human: " + str(boxes))
        return jsonify(
            {
                'boxes': boxes,
                'confidence': confidence
            }
        )
