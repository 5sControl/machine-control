import os
from run import run_machine_control
from machine_control_utils.utils import create_logger
from machine_control_utils.HTTPLIB2Capture import HTTPLIB2Capture
from dotenv import load_dotenv
import warnings

warnings.filterwarnings("ignore")

load_dotenv("config/.env")

username = os.environ.get("username")
password = os.environ.get("password")
folder = os.environ.get("folder")
extra = os.environ.get("extra")
source = os.environ.get("camera_url")
server_url = os.environ.get("server_url")


logger = create_logger()
dataset = HTTPLIB2Capture(source, username=username, password=password)

run_machine_control(dataset, logger, extra, server_url, folder)
