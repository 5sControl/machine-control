from machine_control_utils.model import Model
from machine_control_utils.utils import send_report_and_save_photo
from run import run_camera, run_local, run_example
import warnings
from dotenv import load_dotenv

load_dotenv()

warnings.filterwarnings("ignore")


model_path = "model/yolov8x.xml"
person_conf = 0.35
n_images = 10

model = Model(model_path, person_conf, n_images)


run_camera(model)
# run_local(model)
# run_example(model)
