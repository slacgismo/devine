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
conda activate powerflex_data_env
```

## Stopping the env
```
conda deactivate
```

## Running Script
Use username and password for powerflex login as arugments
```
python data_collection.py {username} {password}
```
