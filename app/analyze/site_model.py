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
        
    def gmm_fit(self, df, stats_dict, show_graph): 
        num_bins = 96
        fig, ax = plt.subplots(4, figsize = (10,20))
        ax_idx = 0
        for key in self.avg_stats_dict.keys():
            # data_points = df[stats_dict[key]]
            data_points = self.avg_stats_dict[key]
            # num_points = np.sum(data_points)
            raw_data = []
            for idx, val in enumerate(data_points):
                for i in range(int(val)):
                    raw_data.append(idx)
            # dp_sum = np.sum(raw_data)
            # dp_mu = np.mean(raw_data)
            # dp_std = np.std(raw_data)
            # dp_filter = [x for x in data_points if x < 100]
            n, bins, patches = ax[ax_idx].hist(raw_data, bins = num_bins, density=True)
            ax[ax_idx].set_title(key)
            (mu, sigma) = norm.fit(raw_data)
            y = norm.pdf(bins, mu, sigma)
            # store bins, mu,sigma
            ax[ax_idx].plot(bins, y, 'r--', linewidth=2)
            self.gmm[key] = (bins, mu, sigma)
            ax_idx += 1
        if show_graph:
                # plt.plot(bins, y, 'r--', linewidth=2)
                path = 'SITE/'
                if not os.path.exists(path):
                    os.makedirs(path)
                plt.savefig(path + self.name + '-' + 'GMM' +  '.png', bbox_inches='tight')

    def update(self, stats_key, df_column):
        (unique, counts) = np.unique(df_column, return_counts=True)
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
    
    def read_data_from_file(self, file_path, show_graph = False):
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
        self.gmm_fit(data2, stats_dict, show_graph)

    def to_graph(self, save_fig = False):
        dict_plot_label = {'xlabel': 'Hour', 'ylabel': 'Frequency', 'title': self.name}
        start_inds = np.arange(0, 96) * 0.25
        # intervals = np.arange(0, 96, 0.01) * 0.25

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
            ax_idx += 1
        if save_fig:
            path = 'SITE/'
            if not os.path.exists(path):
                os.makedirs(path)
            plt.savefig(path + dict_plot_label['title'] + '.png', bbox_inches='tight')
        else:
            plt.show()