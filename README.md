# Machine control: v1.2.5

## Docker 

### Build image for machine_control_python algorithm
- For x86 users

    ```docker build -t 5scontrol/machine_control_python:v1.2.9 .```

- for AArch64 users 

    ```docker buildx build --platform linux/amd64 -t 5scontrol/machine_control_python:v1.2.9 .```

### Build image for machine_control_python_server_model algorithm

- For x86 users

    ```docker build -t 5scontrol/machine_control_python_model_server:v1.0.0 .```

- For AArch64 users 

    ```docker buildx build --platform linux/amd64 -t 5scontrol/machine_control_python_model_server:v1.0.0 .```

### Run containers

*Check id of container:* ```docker image list```

- For machine_control_python

    ```docker run -e username=admin -e password=just4Taqtile -e camera_url="http://192.168.1.163/onvif-http/snapshot?Profile_1" -e server_url=http://192.168.1.110 -e folder=images/192.168.1.163 -it <container>```

- For machine_control_python_server_model

    ```docker run -it <container>```

### Push images

- For machine_control_python:

  ```docker image push machine_control_python:v1.2.9```

- For machine_control_python_server_model:

  ```docker image push machine_control_python_server_model:v1.0.0```

---

**Request**: https://github.com/5sControl/QA_documentation/blob/main/algorithms/run_machine-control.json

**Responce**: https://github.com/5sControl/QA_documentation/blob/main/algorithms/report-with-photos_machine-control.json

- You have to download models:

**Models**: https://drive.google.com/file/d/1oHgIA6D8vgOfWl5AjyclPMvl21Vj_O_G/view?usp=sharing

