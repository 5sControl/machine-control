import httplib2
import numpy as np
import cv2
import logging
import time


class HTTPLIB2Capture:
    def __init__(self, path, **kwargs):
        self.h = httplib2.Http(".cache")
        self.camera_url = path
        self.username = kwargs.get("username", None)
        self.password = kwargs.get("password", None)
        self.h.add_credentials(self.username, self.password)
        if self.username is None or self.password is None:
            logging.warning("Empty password or username")

    def get_snapshots(self, n_images=1) -> list:
        imgs = [None] * n_images
        counter = 0 
        while counter < n_images:
            img = self.try_get_snapshot()
            if img is None:
                continue
            imgs[counter] = img
            counter += 1
        return imgs

    def try_get_snapshot(self):
        try:
            resp, content = self.h.request(self.camera_url, "GET", body="foobar")
            img_array = np.frombuffer(content, np.uint8)
            image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            return image
        except Exception:
            logging.warning("Empty image. Skipping iteration...")
            return None
