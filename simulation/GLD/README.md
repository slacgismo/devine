This folder contains the simulation models.

Docker image to use: `slacgismo/gridlabd`
Docker tag: `latest`

Command to get the docker image: `docker pull slacgismo/gridlabd:latest`

To run the simulation: `docker run -itv [path to model file]:/model slacgismo/gridlabd:latest`

This will create a new linux container based on the image specified. You will now be in the /tmp folder of the container 

Traverse to /model folder (`cd ..` followed by `cd /model`)

To run the simulation...

`sh main.sh`

- main.sh runs the main python file, which spins up the gridlabd model
- gridlabd model contains a custom python file that can do the controls (EV_controls.py)
- Start and stop times can be defined in `config/local.glm` otherwise the defaults set in `config/default.glm` will drive the simulation

Other notes, 

- property `heartbeat 10` will set the simulation to solve every 10 seconds. Note, check the timestamp before invoking controls since intermediate solves will be present.


