import requests
import numpy as np
import time
import cv2
from logging import Logger


class HTTPLIB2Capture:
    def __init__(self, path: str, logger: Logger, **kwargs):
        self.camera_url = path
        self.logger = logger
        self.username = kwargs.get("username", None)
        self.password = kwargs.get("password", None)

        self.is_local = self.camera_url == 'local'

        if self.is_local:
            self.cap = cv2.VideoCapture(1)

        if self.username is None or self.password is None:
            self.logger.warning("Empty password or username")

    def get_snapshot(self):
        img = None
        while img is None:
            self.logger.info('Trying to get photo')
            img = self._get_snapshot_local() if self.is_local else self._get_snapshot_camera()
            if img is None:
                time.sleep(0.5)
        self.logger.info('Got image from camera')
        return img

    def _get_snapshot_local(self):
        succes, img = self.cap.read()
        return img if succes else None

    def _get_snapshot_camera(self):
        try:
            resp = requests.get(self.camera_url)
            img_array = np.frombuffer(resp.content, np.uint8)
            image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            return image
        except Exception as exc:
            self.logger.warning(f"Empty image.\n {exc} \n Skipping iteration...")
            return None
