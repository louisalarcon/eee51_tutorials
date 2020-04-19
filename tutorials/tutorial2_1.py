#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 19 15:15:35 2020

@author: louis
"""

import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import numpy as np
import math
from statistics import mean
import eee51, g51 

# load constants and global variables, referenced by g51.*
g51.init_global_constants()

# run ngspice
cfg = {
        'spice' : '/Applications/ngspice/bin/ngspice', 
        'cir_dir' : '/Users/louis/Documents/UPEEEI/Classes/EEE 51/Mini Projects/',
        'cir_file' : 'circuit2.sp',
        'transfer_data' : 'bjt_transfer_sim.dat',
        'output_data' : 'bjt_output_sim.dat'
        }

# note: you can do this from the command line and just process the data files
# this was done here for convenience
eee51.run_spice(cfg)

# open the output characteristics data file and get the data
vbe = np.linspace(0.65, 0.7, 6, endpoint=True)     # from the simulation setup
vce = []    # declare an empty list to store vce data
ic = [[] for v in range(len(vbe))]  # declare a 2d array to store the currents
                                    # for the different values of vbe

# read the data file
# you can open the data file produced by ngspice and examine the file format
m = 0
with open(cfg['output_data'], 'r') as f:
    for i, line in enumerate(f):
        
        if i == 0:
            vswp0 = float(line.split()[0])
        
        vswp = float(line.split()[0])
        
        if i != 0 and vswp == vswp0:
            m += 1

        if m == 0:
            vce.append(vswp)
            
        ic[m].append(float(line.split()[1]))

# fit the data to the ideal BJT out characteristic and find the Early Voltage (VA)
# fit the line over the linear range of the curves 
# e.g. from 1V to 4V
ind1, vce1 = eee51.find_in_data(vce, 1)
ind4, vce4 = eee51.find_in_data(vce, 4) 

line_m = []     # declare an array of 'slopes'
line_b = []     # declare an array of 'y-intercepts'
line_VA = []    # declare an array of 'x-intercepts' or in this case, VA

# use curve_fit to get the slopes and y-intercepts then caculate VA
for j, v in enumerate(vbe):
    popt, pcov = curve_fit(eee51.line_eq, vce[ind1:ind4], ic[j][ind1:ind4])
    line_m.append(popt[0])
    line_b.append(popt[1])
    line_VA.append(-popt[1]/popt[0])

# declare the x values for plotting the curve-fitted lines
line_x = np.linspace(math.floor(min(line_VA)), max(vce), 100)
g51.update_bjt_VA(mean(line_VA))     
# use the mean value of VA
# yay! we got an estimate for VA

# define the plot parameters
plt_cfg = {
        'grid_linestyle' : 'dotted',
        'title' : 'BJT 2N2222A Output Characteristics (sim)',
        'xlabel' : r'$V_{CE}$ [V]',
        'ylabel' : r'$I_C$ [mA]',
        'legend_loc' : 'upper left',
        'add_legend' : False
        }

# plot the output characteristics
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)

for m, v in enumerate(vbe):
    ax.plot(vce, eee51.scale_vec(ic[m], g51.milli), \
        label = '{:.2f}V'.format(v))

eee51.add_vline_text(ax, 0.2, 1.3, r'$V_{CE,sat}$=' + '{:.1f}V'.format(0.2))

# reorder the legend entries for easier reading
handles, labels = ax.get_legend_handles_labels()
ax.legend(handles[::-1], labels[::-1], title='$V_{BE}$', bbox_to_anchor=(1, 1))

eee51.label_plot(plt_cfg, fig, ax)
plt.savefig('2N2222A_output.png')

# plot the output characteristics and curve-fitted lines to show VA
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)

for m, v in enumerate(vbe):
    ax.plot(vce, eee51.scale_vec(ic[m], g51.milli), \
        label = '{:.2f}V'.format(v))

# plot the curve-fitted lines
for m, b in zip(line_m, line_b):
    ax.plot(line_x, eee51.scale_vec(eee51.line_eq(line_x, m, b), g51.milli), \
        '-.', color='gray', linewidth='0.5')

eee51.add_vline_text(ax, g51.bjt_VA, 0.5, r'$V_A$={:.1f}V'.format(g51.bjt_VA))

# reorder the legend entries for easier reading
handles, labels = ax.get_legend_handles_labels()
ax.legend(handles[::-1], labels[::-1], title='$V_{BE}$', bbox_to_anchor=(1, 1))
eee51.label_plot(plt_cfg, fig, ax)
plt.savefig('2N2222A_output_VA.png')

