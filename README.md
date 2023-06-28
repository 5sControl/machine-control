# machine control

# TODO: rewrite readme

Structure:

<img width="221" alt="image" src="https://github.com/5sControl/machine_control_python/assets/52838912/ee7a68b9-8c36-4060-8a10-8bfc7f04ed41">



Models:

https://drive.google.com/file/d/1oHgIA6D8vgOfWl5AjyclPMvl21Vj_O_G/view?usp=sharing


Get started:

```docker build -t 5scontrol/machine_control_python:v1.1.1 .```

```docker run -e username=admin -e password=just4Taqtile -e camera_url="http://192.168.1.163/onvif-http/snapshot?Profile_1" -e server_url=http://192.168.1.110 -e folder=images/192.168.1.163 -it <container>```

-e extra=[{"coords": [{"x1": 10, "x2": 1000, "y1": 100, "y2": 1000, "zoneName": "zone 51", "zoneId": 51 }] }, { "coords": [{ "x1": 1050, "x2": 2000, "y1": 0, "y2": 1000, "zoneName": "zone 52", "zoneId": 52 }]}]


docker run -e username=admin -e password=just4Taqtile -e camera_url="http://192.168.1.163/onvif-http/snapshot?Profile_1" -e server_url=http://192.168.1.110 -e folder=images/192.168.1.163 -e extra='[{"coords": [{"x1": 10, "x2": 1000, "y1": 100, "y2": 1000, "zoneName": "zone 51", "zoneId": 51 }] }, { "coords": [{ "x1": 1050, "x2": 2000, "y1": 0, "y2": 1000, "zoneName": "zone 52", "zoneId": 52 }]}]' -it bfdadb5f2fea


[optional]: -e extra=[...]

Request: https://github.com/5sControl/QA_documentation/blob/main/algorithms/run_machine-control.json

Responce: https://github.com/5sControl/QA_documentation/blob/main/algorithms/report-with-photos_machine-control.json
