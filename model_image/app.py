from ObjectDetectionModel import YoloDetector
from flask_config.load_config import *
import logging
import colorlog
import numpy as np
from PIL import Image
import io
from flask import Flask, request, jsonify
from concurrent.futures import ThreadPoolExecutor


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


app = Flask(__name__)
model = YoloDetector(MODEL_PATH, PERSOR_CONF)
convert_bytes2image = lambda bytes: np.array(Image.open(io.BytesIO(bytes)), dtype=np.uint8)
executor = ThreadPoolExecutor(max_workers=1)


def process_request(request_data):
    img = convert_bytes2image(request_data)
    boxes, confidence = model.predict(img)
    return boxes, confidence


@app.route("/predict_human", methods=["POST"])
async def predict_human():
    if request.method == "POST":
        request_data = request.files["img"].read()

        future = executor.submit(process_request, request_data)
        boxes, confidence = future.result()
        logger.info("Request to predict_human: Success")
        return jsonify(
            {
                "boxes": boxes.tolist(),
                "confidence": confidence.tolist()
            }
        )


if __name__ == "__main__":
    app.run()
