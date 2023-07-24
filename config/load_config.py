import json


with open("config/config.json", "r") as conf:
    config = json.load(conf)
    TIMEDELTA_MINUTES = config.get("intersection_threshold")
    INTERSECTION_THRESHOLD = config.get("intersection_threshold")
