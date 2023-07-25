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
# source = os.environ.get("camera_url")
source = 'local'
server_url = os.environ.get("server_url")
folder = os.environ.get("folder")
extra = os.environ.get("extra")


logger = create_logger()
dataset = HTTPLIB2Capture(source, username=username, password=password)

run_machine_control(dataset, logger, extra, server_url, folder)
