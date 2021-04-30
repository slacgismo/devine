gridlabd --version
### Check if a directory does not exist ###
if [ ! -d "output/" ] 
then
    mkdir output
fi
python3 -m pip install -r requirements.txt
python3 main.py

