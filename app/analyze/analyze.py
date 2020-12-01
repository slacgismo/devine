import sys
import os
import numpy as np
from site_model import SITE
from driver_model import DRIVER

stats = {
    'Charging Duration': np.zeros(96,), 
    'Arrival': np.zeros(96,), 
    'Departure': np.zeros(96,),
    'Session Duration': np.zeros(96,)
}

Data_path = './historical_data/'
Groups = ['slac_GISMO', 'slac_B53', 'google_plymouth', 'google_B46', 'google_CRIT']
Group_data = {
    'SLAC' : [
        # 'app/analyze/historical_data/SLAC-Session-Details-Meter-with-Summary-2018.csv',
        # 'SLAC-Session-Details-Meter-with-Summary-2019.csv'
    ],
    'Google-Plymouth': [
        # 'app/analyze/historical_data/Plymouth 2019 Session-Details-Meter-with-Summary.csv',
        # 'Plymouth 2020 Session-Details-Meter-with-Summary.csv'
    ],
    'Google-B46':[
        # 'app/analyze/historical_data/MTV-46-2020 Session-Details-Meter-with-Summary.csv',
        #'app/analyze/historical_data/MTV-46-2019 Session-Details-Meter-with-Summary.csv',
        'MTV-46-2018 Session-Details-Meter-with-Summary.csv'
    ],
    'Google-CRIT' :[
        # 'app/analyze/historical_data/MTV-CRIT-2018-Session-Details-Meter-with-Summary',
        # 'app/analyze/historical_data/MTV-CRIT-2019-Session-Details-Meter-with-Summary',
        # 'MTV-CRIT-2020-Session-Details-Meter-with-Summary',
    ]
}


class ANALYZE:
    def __init__(self):
        self.site_models = {}
        self.driver_model = DRIVER(stats)

    def setup(self, path_to_data_folder):
        for site_name in Group_data.keys():
            self.site_models[site_name] = SITE(site_name, stats)
            for site_historical_file in Group_data[site_name]:
                path = path_to_data_folder + site_historical_file
                self.site_models[site_name].read_data_from_file(path, False)
                self.driver_model.read_data_from_file(path)

        for site_model in self.site_models.keys():
            self.site_models[site_model].to_graph(True)
if __name__ == '__main__':
    ANALYZE().setup(Data_path)
