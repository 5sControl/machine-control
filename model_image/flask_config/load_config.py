import json
# from dotenv import load_dotenv
#
# load_dotenv("flask_config/.env")

with open("flask_config/flask_config.json", "r") as conf:
    configs = json.load(conf)
    MODEL_PATH = configs.get("model_path")
    PERSOR_CONF = configs.get("person_conf")
