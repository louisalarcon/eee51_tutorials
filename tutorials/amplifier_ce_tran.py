#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 18 15:42:29 2020

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
        'cir_file' : 'amplifier_ce.sp',
        'transient_data' : 'ce_amp_transient_sim.dat'
        }

# note: you can do this from the command line and just process the data files
# this was done here for convenience
eee51.run_spice(cfg)

# open the transfer characteristics data file and get the data
t = []   # declare list for the time variable
vin = []    # declare list for vin
vout = []   # declare a list for vout

with open(cfg['transient_data'], 'r') as f:
    for line in f:
        t.append(float(line.split()[0]))
        vin.append(float(line.split()[1]))
        vout.append(float(line.split()[3]))
        
vinpp = max(vin) - min(vin)
voutpp = max(vout) - min(vout)

# define the plot parameters
plt_cfg = {
        'grid_linestyle' : 'dotted',
        'title' : r'Common Emitter Amplifier DC Transient Response',
        'xlabel' : r'Time [ms]',
        'ylabel' : r'Voltage [V]',
        'legend_loc' : 'upper left',
        'add_legend' : True,
        'legend_title' : None
        }

# plot the amplifier transfer characteristics
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)

ax.plot(eee51.scale_vec(t, g51.milli), vin, '-', \
    label = r'$v_{IN}$ = ' + '{:.2f} '.format(vinpp/g51.milli) + r'$mV_{p-p}$')

ax.plot(eee51.scale_vec(t, g51.milli), vout, '-', \
    label = r'$v_{OUT}$ = ' + '{:.2f} '.format(voutpp) + r'$V_{p-p}$')

ax.set_ylim(0, 5)

eee51.add_hline_text(ax, 682.7e-3, 0, \
    r'$V_{IN}=$' + '{:.2f}mV'.format(682.7))

eee51.add_hline_text(ax, 2.58, 0, \
    r'$V_{OUT}=$' + '{:.2f}V'.format(2.58))

ax.text(3.1, 4.5, r'$a_v=\frac{V_{OUT,p-p}}{V_{IN,p-p}}=$' + \
    '{:.2f}'.format(voutpp/vinpp))

eee51.label_plot(plt_cfg, fig, ax)
plt.savefig('2N2222A_ce_transient.png')


# define the plot parameters
plt_cfg = {
        'grid_linestyle' : 'dotted',
        'title' : r'Common Emitter Amplifier DC Transient Response',
        'xlabel' : r'Time [ms]',
        'ylabel' : r'$V_{OUT}$ [V]',
        'legend_loc' : 'upper left',
        'add_legend' : True,
        'legend_title' : None
        }

# plot the amplifier transfer characteristics
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
ax2 = ax.twinx()

ax2.plot(eee51.scale_vec(t, g51.milli), eee51.scale_vec(vin, g51.milli), '-', \
    label = r'$v_{IN}$ = ' + '{:.2f} '.format(vinpp/g51.milli) + r'$mV_{p-p}$')

ax.plot(eee51.scale_vec(t, g51.milli), vout, '-', color = 'orangered', \
    label = r'$v_{OUT}$ = ' + '{:.2f} '.format(voutpp) + r'$V_{p-p}$')

ax2.set_ylabel(r'$V_{IN}$ [mV]')
ax2.legend(loc='upper right')

ax.set_ylim(0, 5)
ax2.set_ylim(650, 900)


eee51.add_hline_text(ax2, 682.7, 3.75, \
    r'$V_{IN}=$' + '{:.2f}mV'.format(682.7))

eee51.add_hline_text(ax, 2.58, 0, \
    r'$V_{OUT}=$' + '{:.2f}V'.format(2.58))

ax.text(0, 4, r'$a_v=\frac{V_{OUT,p-p}}{V_{IN,p-p}}=$' + \
    '{:.2f}'.format(voutpp/vinpp))

eee51.label_plot(plt_cfg, fig, ax)
plt.savefig('2N2222A_ce_transient_zoom.png')


# ideal sinusoid
am = 1.43/2
w = 2 * np.pi * 1e3
ideal_sin = [-am * np.sin(w * tx) + 2.58 for tx in t]

# define the plot parameters
plt_cfg = {
        'grid_linestyle' : 'dotted',
        'title' : r'Common Emitter Amplifier DC Transient Response',
        'xlabel' : r'Time [ms]',
        'ylabel' : r'$V_{OUT}$ [V]',
        'legend_loc' : 'upper left',
        'add_legend' : True,
        'legend_title' : None
        }

# plot the amplifier transfer characteristics
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)


ax.plot(eee51.scale_vec(t, g51.milli), vout, '-', \
    label = r'$v_{OUT}$ = ' + '{:.2f} '.format(voutpp) + r'$V_{p-p}$')

ax.plot(eee51.scale_vec(t, g51.milli), ideal_sin, '--', \
    label = r'ideal sinusoid')

ax.set_ylim(1, 4)

eee51.add_hline_text(ax, 2.58, 0, \
    r'$V_{OUT}=$' + '{:.2f}V'.format(2.58))

eee51.label_plot(plt_cfg, fig, ax)
plt.savefig('2N2222A_ce_transient_output_disto.png')

