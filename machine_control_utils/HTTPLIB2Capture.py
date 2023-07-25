import httplib2
import numpy as np
import cv2
import logging
import time


class HTTPLIB2Capture:
    def __init__(self, path, **kwargs):
        self.camera_url = path
        self.username = kwargs.get("username", None)
        self.password = kwargs.get("password", None)

        self.is_local = self.camera_url == 'local'

        if self.is_local:
            self.cap = cv2.VideoCapture(1)
        else:
            self.h = httplib2.Http(".cache")
            self.h.add_credentials(self.username, self.password)

        if self.username is None or self.password is None:
            logging.warning("Empty password or username")

    def get_snapshot(self):
        if self.is_local:
            return self.get_snapshot_local()
        else:
            return self.get_snapshot_camera()

    def get_snapshot_local(self):
        succes, img = self.cap.read()
        if succes:
            cv2.imshow("img", img)
            if cv2.waitKey(1) & 0xFF == 27:
                return None
            return img


        # cap = cv2.VideoCapture(1)
        # succes, img = cap.read()
        # areas_data = get_areas(img.shape)
        #
        # while True:
        #     succes, img = cap.read()
        #     if succes:
        #         run_machine_control(img, areas_data, logger)
        #         cv2.imshow("img", img)
        #     if cv2.waitKey(1) & 0xFF == 27:
        #         break
        #     cv2.imshow("img", img)
        #
        # cap.release()
        # cv2.destroyAllWindows()


    def get_snapshot_camera(self):
        while True:
            img = self.try_get_snapshot()
            if img is None:
                continue
            return img

    def try_get_snapshot(self):
        try:
            resp, content = self.h.request(self.camera_url, "GET", body="foobar")
            img_array = np.frombuffer(content, np.uint8)
            image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            return image
        except Exception:
            logging.warning("Empty image. Skipping iteration...")
            return None
