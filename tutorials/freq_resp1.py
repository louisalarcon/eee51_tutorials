#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 17 15:27:57 2020

@author: louis
"""

import matplotlib.pyplot as plt
import numpy as np
import eee51, g51 

# load constants
g51.init_global_constants()


# run ngspice
cfg = {
        'spice' : '/Applications/ngspice/bin/ngspice', 
        'cir_dir' : '/Users/louis/Documents/UPEEEI/Classes/EEE 51/Mini Projects/',
        'cir_file' : 'bjt_2n3904_ft.sp',
        'ac_sim_1mA' : 'bjt_2n3904_ft_1mA_sim.dat',
        'ac_sim_10mA' : 'bjt_2n3904_ft_10mA_sim.dat'
        }

# note: you can do this from the command line and just process the data files
# this was done here for convenience
eee51.run_spice(cfg)

# define the plot parameters
plt_cfg = {
        'grid_linestyle' : 'dotted',
        'title' : r'2N3904 Transition Frequency ($f_T$)',
        'xlabel' : r'Frequency [Hz]',
        'ylabel' : r'Current Gain ($\beta$) [dB]',
        'legend_loc' : 'lower left',
        'add_legend' : True,
        'legend_title' : None
        }

fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)

eee51.add_hline_text(ax, 0, 1e5, \
    r'{:.1f}dB'.format(0))

ic_labels = [r'$I_C = 1mA$', r'$I_C = 10mA$']
files = [cfg['ac_sim_1mA'], cfg['ac_sim_10mA']]
for file, ic_label in zip(files, ic_labels):
    
    freq = []
    ic1 = []
    
    with open(file, 'r') as f:
        for line in f:
            freq.append(float(line.split()[0]))
            ic1_real = float(line.split()[1])
            ic1_imag = float(line.split()[2])
            
            ic1.append(((ic1_real**2) + (ic1_imag**2))**0.5)

    index, ic1_sim = eee51.find_in_data(ic1, 1.0)

    ax.semilogx(freq, 20*np.log10(ic1), '-', \
        label = ic_label)

    eee51.add_vline_text(ax, freq[index], 20, \
        '{:.2f}MHz'.format(freq[index]/1e6))
    
eee51.label_plot(plt_cfg, fig, ax)
plt.savefig('bjt_2n3904_ft.png')
