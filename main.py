from run import run_machine_control, run_camera, run_local
from machine_control_utils.utils import create_logger

import warnings

warnings.filterwarnings("ignore")

logger = create_logger()


# run_camera(model)
run_local(logger)
# run_example(model)
