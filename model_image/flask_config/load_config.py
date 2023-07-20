import json
from dotenv import load_dotenv

load_dotenv("confs/.env")

with open("confs/configs.json", "r") as conf:
    configs = json.load(conf)
    MODEL_PATH = configs.get("person_conf")
    PERSOR_CONF = configs.get("model_path")
