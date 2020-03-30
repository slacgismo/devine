# power-flex data collection
This folder contains the code for data collection from powerflex.

# Getting Setup

## Creating the env - ensure you are running the anaconda `4.5.x +`
```
conda env create -f environment.yml
```

## Updating the env after adding new packages
```
conda env update -f environment.yml
```

## Starting the env
```
conda activate venv_devine
```

## Stopping the env
```
conda deactivate
```

## Running Script - assumes you have AWS credentials in your env
Use username and password for powerflex login as arugments
```bash
export USERNAME="" # set the username
export PASSWORD="" # set the password
export DEBUG="" # set the debug flag
export INTERVAL=True|False # set the interval flag
export SESSION=True|False # set the session flag
python ingest.py 

# you could, conversely, pass in these as command line arguments to the script
# python ingest.py use_args [unam] [pswwd] [interval] [session] [debug]
python ingest.py use_args hi@hi.com 1234 True True False
```

## Build & Run Docker container
```bash
docker build -t devine-data-ingest .
docker run -e USERNAME=the_username -e PASSWORD=thepassword -e DEBUG=debug -e AWS_ACCESS_KEY_ID=asdf -e AWS_SECRET_ACCESS_KEY=asdf devine-data-ingest
```