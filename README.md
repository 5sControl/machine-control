# About Machine control
Machine control is one of the Official [5controlS](https://5controls.com/) algorithm.

Designed to handle complex industrial processes with ease, this innovative tool is perfect for use with semi-automated equipment. With Machine Control you can optimize your industrial processes and keep your equipment running smoothly, saving you time and money.

![Frame 2608741](https://github.com/5sControl/machine-control/assets/131950264/5c074f95-2ea6-4247-9aba-5efe944b7188)


## Key features

- monitors use of equipment;
- prevents downtime of valuable and expensive equipment.

**Plug-in Machine control to 5controlS platform to detect when your workers are absent!**

> Learn more about Machine control on the [5controlS website](https://5controls.com/solutions/machine-control).

# Getting started 

### Build image for machine_control_python algorithm
- For x86 users

    ```docker build -t 5scontrol/machine_control_python:latest .```

- for AArch64 users 

    ```docker buildx build --platform linux/amd64 -t 5scontrol/machine_control_python:latest .```


### Build image for machine_control_python_server_model algorithm

- For x86 users

    ```docker build -t 5scontrol/machine_control_python_model_server:latest .```

- For AArch64 users 

    ```docker buildx build --platform linux/amd64 -t 5scontrol/machine_control_python_model_server:latest .```



### Run containers

*Check id of container:* ```docker image list```

- For machine_control_python

    ```docker run -e username=admin -e password=just4Taqtile -e camera_url="http://192.168.1.163/onvif-http/snapshot?Profile_1" -e server_url=http://192.168.1.110 -e folder=images/192.168.1.163 -it <container>```

- For machine_control_python_server_model

    ```docker run -it <container>```


### Run/Test code

- For machine_control_python

  ```python main.py```

- For machine_control_python_server_model

  ```python -m flask run --host 0.0.0.0 --port 5002```


### Push images

- For machine_control_python:

  ```docker image push 5scontrol/machine_control_python:latest```

- For machine_control_python_server_model:

  ```docker image push 5scontrol/machine_control_python_model_server:latest```

[optional]: -e extra=[...]

---

**Request**: https://github.com/5sControl/QA_documentation/blob/main/algorithms/run_machine-control.json

**Responce**: https://github.com/5sControl/QA_documentation/blob/main/algorithms/report-with-photos_machine-control.json

- You have to download models:

**Models**: https://drive.google.com/file/d/1oHgIA6D8vgOfWl5AjyclPMvl21Vj_O_G/view?usp=sharing
you have to download models 

# **Documentation**

[Documentation for Developers](https://github.com/5sControl/5s-dev-documentation/wiki)

[User Documentation](https://github.com/5sControl/Manufacturing-Automatization-Enterprise/wiki)

# **Contributing**
Thank you for considering contributing to 5controlS. We truly believe that we can build an outstanding product together!

We welcome a variety of ways to contribute. Read below to learn how you can take part in improving 5controlS.

## **Code of conduct**

Please note that this project is released with a [Contributor Code of Conduct](CODE_OF_CONDUCT.md). By participating in this project you agree to abide by its terms.

## Code contributing

If you want to contribute, read  our [contributing guide](CONTRIBUTING.md) to learn about our development process and pull requests workflow.

We also have a list of [good first issues](https://github.com/5sControl/machine-control/issues?q=is%3Aopen+is%3Aissue+label%3A%22good+first+issue%22) that will help you make your first step to beсoming a 5S contributor.

# **Project repositories**

**5controlS Platform:**
1. [5s-webserver](https://github.com/5sControl/5s-webserver)
2. [5s-backend](https://github.com/5sControl/5s-backend)
3. [5s-frontend](https://github.com/5sControl/5s-frontend)
4. [5s-algorithms-controller](https://github.com/5sControl/5s-algorithms-controller)
5. [5s-onvif](https://github.com/5sControl/5s-onvif)
6. [5s-onvif-finder](https://github.com/5sControl/5s-onvif-finder)
  
**Official Algorithms:**
1. [min-max](https://github.com/5sControl/min-max)
2. [idle-control](https://github.com/5sControl/idle-control)
3. [operation-control-js](https://github.com/5sControl/operation-control-js)
4. [machine-control](https://github.com/5sControl/machine-control)
5. [machine-control-js](https://github.com/5sControl/machine-control-js)

**Algorithms Servers:**
1. [inference-server-js](https://github.com/5sControl/inference-server-js)

# **License**
[AGPL-3.0](LICENSE)

> Machine control uses third party libraries that are distributed under their own terms (see [LICENSE-3RD-PARTY.md](https://github.com/5sControl/machine-control/blob/main/LICENSE-3RD-PARTY.md)).<br>

<br>
<div align="center">
  <a href="https://5controls.com/" style="text-decoration:none;">
    <img src="https://github.com/5sControl/Manufacturing-Automatization-Enterprise/blob/3bafa5805821a34e8b825df7cc78e00543fd7a58/assets/Property%201%3DVariant4.png" width="10%" alt="" /></a> 
  <img src="https://github.com/5sControl/5s-backend/assets/131950264/d48bcf5c-8aa6-42c4-a47d-5548ae23940d" width="3%" alt="" />
  <a href="https://github.com/5sControl" style="text-decoration:none;">
    <img src="https://github.com/5sControl/Manufacturing-Automatization-Enterprise/blob/3bafa5805821a34e8b825df7cc78e00543fd7a58/assets/github.png" width="4%" alt="" /></a>
  <img src="https://github.com/5sControl/5s-backend/assets/131950264/d48bcf5c-8aa6-42c4-a47d-5548ae23940d" width="3%" alt="" />
  <a href="https://www.youtube.com/@5scontrol" style="text-decoration:none;">
    <img src="https://github.com/5sControl/Manufacturing-Automatization-Enterprise/blob/ebf176c81fdb62d81b2555cb6228adc074f60be0/assets/youtube%20(1).png" width="5%" alt="" /></a>
</div>




