import sys
import numpy as np
from site_model import SITE
from driver_model import DRIVER

stats = {
    'Charging Duration': np.zeros(96,), 
    'Arrival': np.zeros(96,), 
    'Departure': np.zeros(96,),
    'Session Duration': np.zeros(96,)
}

if __name__ == '__main__':
    # print("SITE Name:", sys.argv[1])
    # print("Parsing",len(sys.argv) - 2, "historical data files")
    # file_names = sys.argv[2:]
    file_names = []
    # file_names.append('./historical_data/MTV-46-2020 Session-Details-Meter-with-Summary.csv')
    # file_names.append('./historical_data/MTV-46-2019 Session-Details-Meter-with-Summary.csv')
    file_names.append('./historical_data/MTV-46-2018 Session-Details-Meter-with-Summary.csv')
    site = SITE('Google', stats)
    dirver_stats = DRIVER(stats)
    for file in file_names:
        site.read_data_from_file(file)
        site.to_graph(save_fig = True)

    # for file in file_names:
    #     dirver_stats.read_data_from_file(file)
