import requests
import numpy as np
import cv2
import logging


class HTTPLIB2Capture:
    def __init__(self, path, **kwargs):
        self.camera_url = path
        self.username = kwargs.get("username", None)
        self.password = kwargs.get("password", None)

        self.is_local = self.camera_url == 'local'

        if self.is_local:
            self.cap = cv2.VideoCapture(1)

        if self.username is None or self.password is None:
            logging.warning("Empty password or username")

    def get_snapshot(self):
        if self.is_local:
            return self.get_snapshot_local()
        else:
            return self.get_snapshot_camera()

    def get_snapshot_local(self):
        while True:
            succes, img = self.cap.read()
            if succes:
                return img

    def get_snapshot_camera(self):
        while True:
            img = self.try_get_snapshot()
            if img is None:
                continue
            return img

    def try_get_snapshot(self):
        try:
            resp = requests.get(self.camera_url)
            img_array = np.frombuffer(resp.content, np.uint8)
            image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            return image
        except Exception as exc:
            logging.warning(f"Empty image.\n {exc} \n Skipping iteration...")
            return None
