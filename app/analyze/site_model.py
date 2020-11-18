'''
Site behavior modeling.
Statistics:
1. Average, Standard Deviation of indices
2. GMM model
'''
from analyze_utils import *
from scipy.stats import norm
from matplotlib import pyplot as plt
from scipy.optimize import curve_fit
from scipy.signal import find_peaks
import os
import numpy as np
import pandas as pd

class SITE:
    '''
    avg_stats_dict: key => statistics, value => distribution of the statistics over 24 hours (96 intervals)
    '''
    def __init__(self, name, stats_dict = {}):
        self.name = name
        self.avg_stats_dict = stats_dict
        self.gmm = {}
        for key in self.avg_stats_dict.keys():
            self.gmm[key] = None
        
    def gmm_fit(self, df, stats_dict): 
        num_bins = 96
        for key in self.avg_stats_dict.keys():
            data_points = df[stats_dict[key]]
            dp_filter = [x for x in data_points if x < 100]
            n, bins, patches = plt.hist(dp_filter, bins = num_bins, density=True)
            (mu, sigma) = norm.fit(dp_filter)
            y = norm.pdf(bins, mu, sigma)
            plt.plot(bins, y, 'r--', linewidth=2)
            plt.show()

    def update(self, stats_key, df_column):
        (unique, counts) = np.unique(df_column / 4, return_counts=True)
        freq = np.zeros(96,)

        # Get freq counts over the day
        for idx, j in enumerate(unique):
            if j < len(freq):
                freq[int(j)] = counts[idx]
        
        for idx, i in enumerate(self.avg_stats_dict[stats_key]):
            if freq[idx] != 0:
                self.avg_stats_dict[stats_key][idx] += freq[idx]
        
    def update_statistics(self, stats_key, dataframe):
        self.update(stats_key, dataframe)
    
    def read_data_from_file(self, file_path):
        stats_dict = {
            'Charging Duration': 'Charging Time 15min', 
            'Arrival': 'Start Time 15min', 
            'Departure': 'End Time 15min',
            'Session Duration': 'Total Duration 15min',
        }

        # Get data frame
        print('Reading file', file_path)
        file_data = pd.read_csv(file_path)
        data2 = file_data.copy()
        data2['Total Duration 15min'] = hour2min15(data2['Total Duration (hh:mm:ss)'])
        data2['Charging Time 15min'] = hour2min15(data2['Charging Time (hh:mm:ss)'])
        data2['End Time 15min'] = np.floor(data2['start_seconds']/900 + data2['Total Duration 15min'])
        data2['Start Time 15min'] = np.floor(data2['start_seconds']/900)
        
        # Statistics - overall data:
        total_sessions = len(data2)
        print('Total # of sessions: ', total_sessions)

        # Update site internal statistics
        for key in self.avg_stats_dict.keys():
            self.update_statistics(key, data2[stats_dict[key]])
        
        # update gmm model
        self.gmm_fit(data2, stats_dict)

    def to_graph(self, save_fig = False):
        dict_plot_label = {'xlabel': 'Hour', 'ylabel': 'Frequency', 'title': 'Distribution of site users'}
        start_inds = np.arange(0, 96) * 0.25
        intervals = np.arange(0, 96, 0.01) * 0.25

        fig, ax = plt.subplots(4, figsize = (10,20))
        # fig.set_title(dict_plot_label['title'])
        ax_idx = 0
        for key in self.avg_stats_dict.keys():
            freq = self.avg_stats_dict[key]
            ax[ax_idx].bar(start_inds, freq, alpha=1, edgecolor='k', width=0.2)
            ax[ax_idx].set_xticks(np.arange(0,24,2))
            ax[ax_idx].set_xlabel(dict_plot_label['xlabel'])
            ax[ax_idx].set_ylabel(dict_plot_label['ylabel'])
            ax[ax_idx].set_title(key)
        if save_fig:
            path = 'SITE/'
            if not os.path.exists(path):
                os.makedirs(path)
            plt.savefig(path + dict_plot_label['title'] + '.png', bbox_inches='tight')
        else:
            plt.show()