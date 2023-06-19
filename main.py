import time
import datetime
from functional import *
import cv2
from dotenv import load_dotenv

load_dotenv()

# os.environ["extra"] = '''[
#         {
#           "coords": [{
#             "x1": 10,
#             "x2": 1000,
#             "y1": 100,
#             "y2": 1000,
#             "zoneName": "zone 51",
#             "zoneId": 51
#           }]
#         },
#         {
#           "coords": [{
#             "x1": 1050,
#             "x2": 2000,
#             "y1": 0,
#             "y2": 1000,
#             "zoneName": "zone 52",
#             "zoneId": 52
#           }]
#         }
#       ]'''


def run():
    while (h := init_connection()) is None:
        print('init connection error')
        time.sleep(1)

    while (img := get_frame(h)) is None:
        print('get frame error')
        time.sleep(1)

    area_values = get_areas(img.shape)
    model = init_model()
    itr = 0

    while True:
        time.sleep(1)
        if (img := get_frame(h)) is None: continue
        boxes, confs = predict(model, img)
        for i, a_val in enumerate(area_values):
            x1_area, y1_area, x2_area, y2_area = a_val.coords

            cv2.putText(img, str(a_val.zone_name) + " : " + str(a_val.zone_id), (x1_area, y1_area - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.5, (100, 0, 200), 5, cv2.LINE_AA)
            for (x1, y1, x2, y2), conf in zip(boxes, confs):
                x1, y1 = max(x1, x1_area), max(y1, y1_area)
                x2, y2 = min(x2, x2_area), min(y2, y2_area)

                # draw red area
                cv2.rectangle(img, (x1_area, y1_area), (x2_area, y2_area), (0, 0, 200), 2)
                if x1_area <= x1 <= x2_area and y1_area <= y1 <= y2_area and x1_area <= x2 <= x2_area and y1_area <= y2 <= y2_area:

                    # change to green if person in area
                    cv2.putText(img, str(conf), (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
                    cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), 2)
                    cv2.rectangle(img, (x1_area, y1_area), (x2_area, y2_area), (0, 200, 0), 2)

                    if len(area_values[i].imgs) == 0 or len(area_values[i].imgs) == 3:
                        area_values[i].imgs.append(img)
                        area_values[i].date.append(datetime.datetime.now())

                    if len(area_values[i].imgs) == 1:
                        area_values[i].imgs[0] = img
                        area_values[i].date[0] = datetime.datetime.now()

                else:
                    cv2.rectangle(img, (x1_area, y1_area), (x2_area, y2_area), (0, 0, 200), 2)
                    if len(area_values[i].imgs) == 1:
                        area_values[i].imgs.append(img)
                        area_values[i].date.append(datetime.datetime.now())
                        area_values[i].imgs.append(img)
                        area_values[i].date.append(datetime.datetime.now())

                    if len(area_values[i].imgs) == 3:
                        area_values[i].imgs[2] = img
                        area_values[i].date[2] = datetime.datetime.now()

            if not len(boxes):
                cv2.rectangle(img, (x1_area, y1_area), (x2_area, y2_area), (0, 0, 200), 2)
                if len(area_values[i].imgs) == 1:
                    area_values[i].imgs.append(img)
                    area_values[i].date.append(datetime.datetime.now())
                    area_values[i].imgs.append(img)
                    area_values[i].date.append(datetime.datetime.now())

                if len(area_values[i].imgs) == 3:
                    area_values[i].imgs[2] = img
                    area_values[i].date[2] = datetime.datetime.now()

        for i, _ in enumerate(area_values):
            if len(area_values[i].imgs) >= 4:
                send_report_and_save_photo(area_values[i])

        for i, _ in enumerate(area_values):
            if len(area_values[i].imgs) >= 4:
                area_values[i].imgs = []
                area_values[i].date = []

        # logging:
        if itr % 10 == 0:
            for i, v in enumerate(area_values):
                print(f'zone_id({v.zone_id}): {len(v.imgs)}', end=' ')
            print()
        itr += 1


if __name__ == '__main__':
    run()
