from machine_control_utils.model import YoloDetector
from run import run_camera, run_local, run_example
import warnings
from dotenv import load_dotenv

load_dotenv('config/.env')

warnings.filterwarnings("ignore")


model_path = "model/yolov8x.xml"
person_conf = 0.5
n_images = 1

model = YoloDetector(model_path, person_conf, n_images)


run_camera(model)
# run_local(model)
# run_example(model)
