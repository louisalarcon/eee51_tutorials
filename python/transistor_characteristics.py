#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 16 18:29:11 2020

@author: louis
"""

import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import numpy as np
from si_prefix import si_format
import math
from statistics import mean
import eee51, g51 

# load constants and global variables, referenced by g51.*
g51.init_global_constants()

specs = {
        'ic' : 1e-3,
        'vce' : 2.5
        }
    
# run ngspice
cfg = {
        'spice' : '/Applications/ngspice/bin/ngspice', 
        'cir_dir' : '/Users/louis/Documents/UPEEEI/Classes/EEE 51/Mini Projects/',
        'cir_file' : 'transistor_characteristics.sp',
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
plt.savefig('2N2222A_output.pdf')

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
plt.savefig('2N2222A_output_VA.pdf')

# to get the rest of the BJT parameters, let's use the transfer characteristics
# open the transfer characteristics data file and get the data
vbe = []    # declare list for vbe
ic = []     # declare a list for ic with vce = vce,sat = 0.2V
ic2 = []    # declare a list for ic with vce = 2.5V
            # we'll use this to check our model
ib2 = []    # declare a list for the base currents at vce = 2.5V
            
with open(cfg['transfer_data'], 'r') as f:
    for line in f:
        vbe.append(float(line.split()[0]))
        ic.append(float(line.split()[1]))
        ic2.append(float(line.split()[3]))
        ib2.append(float(line.split()[5]))

# convert to mV and mA
ic_mA = eee51.scale_vec(ic, g51.milli)
vbe_mV = eee51.scale_vec(vbe, g51.milli)

# fit the data to the ideal BJT transfer characteristic and find Is
# fit using the data at vce = 0.2V
g51.update_bjt_vce(0.2)
popt, pcov = curve_fit(eee51.ideal_bjt_transfer, vbe, ic)
bjt_Is = popt[0]    # yay! we get an estimate for Is and n
bjt_n = popt[1]

# generate the ic for the ideal bjt model 
# using our values for Is, n, and VA at vce = 0.2V
ic_ideal = [eee51.ideal_bjt_transfer(v, bjt_Is, bjt_n) for v in vbe]
ic_ideal_mA = eee51.scale_vec(ic_ideal, g51.milli)

# get the value of vbe that will result in a 1mA ic using the simulation results
index_spec_sim, ic_spec_sim = eee51.find_in_data(ic, specs['ic'])
vbe_spec_sim = vbe[index_spec_sim]
vbe_spec_sim_mV = vbe_spec_sim/g51.milli

# get the value of vbe that will result in a 1mA ic using the our model
index_spec_ideal, ic_spec_ideal = eee51.find_in_data(ic_ideal, specs['ic'])
vbe_spec_ideal = vbe[index_spec_ideal]
vbe_spec_ideal_mV = vbe_spec_ideal/g51.milli

plt_cfg = {
        'grid_linestyle' : 'dotted',
        'title' : 'BJT 2N2222A Transfer Characteristics',
        'xlabel' : r'$V_{BE}$ [mV]',
        'ylabel' : r'$I_C$ [mA]',
        'legend_loc' : 'upper left',
        'add_legend' : True,
        'legend_title' : None
        }

# plot the transfer characteristics at 200mV
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
ax.plot(vbe_mV, ic_mA, '--', label = 'simulation ($V_{CE}$=0.2V)')
ax.plot(vbe_mV, ic_ideal_mA, \
    label = 'ideal BJT using $I_S$=' + \
    si_format(bjt_Is, precision=2) + r'A, $n$={:.2f}, and '.format(bjt_n) + \
    r'$|V_A|$={:.2f}'.format(abs(g51.bjt_VA)))

# add_vline_text(ax, vbe_1mA_sim_mV, 3, '{:.1f}mV'.format(vbe_1mA_sim_mV))
eee51.add_vline_text(ax, vbe_spec_ideal_mV, 3, '{:.1f}mV'.format(vbe_spec_ideal_mV))

eee51.add_hline_text(ax, specs['ic']/g51.milli, 550, \
    '{:.1f}mA'.format(specs['ic']/g51.milli))

eee51.label_plot(plt_cfg, fig, ax)
plt.savefig('2N2222A_transfer_200mV.pdf')

# calculate the vbe needed for vce = 2.5V
reqd_vbe = eee51.bjt_find_vbe(specs['ic'], specs['vce'], \
    bjt_Is, bjt_n, g51.bjt_VA)

# generate the ic for the ideal bjt model 
# using our values for Is, n, and VA at vce = 2.5V

g51.update_bjt_vce(specs['vce'])

ic_ideal = [eee51.ideal_bjt_transfer(v, bjt_Is, bjt_n) for v in vbe]
ic_ideal_mA = eee51.scale_vec(ic_ideal, g51.milli)

# plot the transfer characteristics at 2.5V
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
ax.plot(vbe_mV, eee51.scale_vec(ic2, g51.milli), '--', \
    label = 'simulation ($V_{CE}$=2.5V)')
ax.plot(vbe_mV, ic_ideal_mA, \
    label = 'ideal BJT using $I_S$=' + \
    si_format(bjt_Is, precision=2) + r'A, $n$={:.2f}, and '.format(bjt_n) + \
    r'$|V_A|$={:.2f}'.format(abs(g51.bjt_VA)))

eee51.add_vline_text(ax, reqd_vbe/g51.milli, 1.1, 'calculated $V_{BE}$ = ' + \
    '{:.1f}mV'.format(reqd_vbe/g51.milli))

eee51.add_hline_text(ax, specs['ic']/g51.milli, 550, \
    '{:.1f}mA'.format(specs['ic']/g51.milli))

eee51.label_plot(plt_cfg, fig, ax)
plt.savefig('2N2222A_transfer_2500mV.pdf')

# plot the transistor dc beta
bjt_beta = [a/b for a, b in zip(ic2, ib2)]

index, vbe_sim = eee51.find_in_data(vbe, reqd_vbe)

plt_cfg = {
        'grid_linestyle' : 'dotted',
        'title' : r'BJT 2N2222A DC $\beta_{DC}$',
        'xlabel' : r'$V_{BE}$ [mV]',
        'ylabel' : r'$\beta$',
        'legend_loc' : 'upper left',
        'add_legend' : False,
        'legend_title' : None
        }

fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
ax.plot(vbe_mV, bjt_beta, \
    label = 'simulation ($V_{CE}$=2.5V)')

eee51.add_vline_text(ax, reqd_vbe/g51.milli, 10, '$V_{BE}$ = ' + \
    '{:.1f}mV'.format(reqd_vbe/g51.milli))

eee51.add_hline_text(ax, bjt_beta[index], 550, \
    r'$\beta_{DC}=$' + '{:.2f}'.format(bjt_beta[index]))

eee51.label_plot(plt_cfg, fig, ax)
plt.savefig('2N2222A_beta_dc.pdf')

