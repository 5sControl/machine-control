# Machine control: v1.2.5

## Docker 

### build image
* for x86 users

    ```docker build -t 5scontrol/machine_control_python:v1.2.5 .```

* for AArch64 users 

    ```docker buildx build --platform linux/amd64 -t 5scontrol/machine_control_python:v1.2.5 .```

### run container
    ```docker run -e username=admin -e password=just4Taqtile -e camera_url="http://192.168.1.163/onvif-http/snapshot?Profile_1" -e server_url=http://192.168.1.110 -e folder=images/192.168.1.163 -it <container>```

[optional]: -e extra=[...]

---

**Request**: https://github.com/5sControl/QA_documentation/blob/main/algorithms/run_machine-control.json

**Responce**: https://github.com/5sControl/QA_documentation/blob/main/algorithms/report-with-photos_machine-control.json

**Models**: https://drive.google.com/file/d/1oHgIA6D8vgOfWl5AjyclPMvl21Vj_O_G/view?usp=sharing
you have to download models 
