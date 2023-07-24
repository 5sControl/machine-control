import json
from dotenv import load_dotenv

load_dotenv("flask_config.json/.env")

with open("flask_config/flask_configs.json", "r") as conf:
    configs = json.load(conf)
    MODEL_PATH = configs.get("person_conf")
    PERSOR_CONF = configs.get("model_path")
