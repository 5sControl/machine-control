from flask import Flask, jsonify, request
from ObjectDetectionModel import YoloDetector
from flask_config.load_config import *


app = Flask(__name__)
model = YoloDetector(MODEL_PATH, PERSOR_CONF)


@app.route('/predict_human', methods=['POST'])
def predict_human():
    if request.method == 'POST':
        img = request.json['img']
        boxes, confidence = model.predict(img)
        return jsonify(
            {
                'boxes': boxes,
                'confidence': confidence
            }
        )
