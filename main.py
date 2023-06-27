from deep_sort_realtime.deepsort_tracker import DeepSort
from machine_control_utils.model import Model
from machine_control_utils.utils import send_report_and_save_photo
from run import run_camera, run_local, run_example
import warnings
from dotenv import load_dotenv

load_dotenv()

warnings.filterwarnings("ignore")


model_path = "model/yolov8n.xml"
person_conf = 0.4

model = Model(model_path, person_conf)


run_camera(model)
# run_local(model)
# run_example(model)


# extra=[{"coords": [{"x1": 10, "x2": 1000, "y1": 100, "y2": 1000, "zoneName": "zone 51", "zoneId": 51 }] }, { "coords": [{ "x1": 1050, "x2": 2000, "y1": 0, "y2": 1000, "zoneName": "zone 52", "zoneId": 52 }] } ]

# object_tracker = DeepSort(
#     max_age=5,
#     n_init=2,
#     nms_max_overlap=1.0,
#     max_cosine_distance=0.3,
#     nn_budget=None,
#     override_track_class=None,
#     embedder="mobilenet",
#     half=True,
#     bgr=True,
#     embedder_gpu=False,
#     embedder_model_name=None,
#     embedder_wts=None,
#     polygon=False,
#     today=None,
# )
