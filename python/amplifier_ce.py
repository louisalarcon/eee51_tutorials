#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 18 12:07:00 2020

@author: louis
"""

import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import numpy as np
from si_prefix import si_format
import math
from statistics import mean
import eee51, g51 

# load constants
g51.init_global_constants()

# run ngspice
cfg = {
        'spice' : '/Applications/ngspice/bin/ngspice', 
        'cir_dir' : '/Users/louis/Documents/UPEEEI/Classes/EEE 51/Mini Projects/',
        'cir_file' : 'amplifier_ce.sp',
        'transfer_data' : 'ce_amp_transfer_sim.dat'
        }

# note: you can do this from the command line and just process the data files
# this was done here for convenience
eee51.run_spice(cfg)

# open the transfer characteristics data file and get the data
vin = []    # declare list for vin
vout = []   # declare a list for vout
ic = []     # declare a list for ic

with open(cfg['transfer_data'], 'r') as f:
    for line in f:
        vin.append(float(line.split()[0]))
        vout.append(float(line.split()[1]))
        ic.append(float(line.split()[3]))
        
bjt_n = 1.2610858394025979
reqd_vbe = 682.73e-3
Rc = 2.5e3
g51.update_bjt_VA(-15.550605626760145) 

index, vin_sim = eee51.find_in_data(vin, 0.0)
vo_dc = vout[index]
ro_calc = abs(g51.bjt_VA) / ic[index] 

gm_calc = ic[index]/(bjt_n * g51.VT)
gain_calc = -gm_calc * eee51.r_parallel([Rc, ro_calc])

# define the plot parameters
plt_cfg = {
        'grid_linestyle' : 'dotted',
        'title' : r'Common Emitter Amplifier DC Transfer Curve',
        'xlabel' : r'$v_{in}$ [mV]',
        'ylabel' : r'$v_{out}$ [V]',
        'legend_loc' : 'upper left',
        'add_legend' : True,
        'legend_title' : None
        }

# plot the amplifier transfer characteristics
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
ax.plot(eee51.scale_vec(vin, g51.milli), vout, '--', \
    label = r'$v_{OUT}$ with $R_C=$2.5 k$\Omega$')

ax2 = ax.twinx()
ax2.set_ylabel(r'$I_C$ [mA]')
ax2.plot(eee51.scale_vec(vin, g51.milli), eee51.scale_vec(ic, g51.milli), \
         ':', color='orangered', label = r'$I_C$')
ax2.legend(loc='upper right')


eee51.add_vline_text(ax, 0, 0, r'$V_{BE}$ = ' + \
    '{:.1f}mV'.format(reqd_vbe/g51.milli))

eee51.add_hline_text(ax, vo_dc, -75, \
    r'$V_{OUT}=$' + '{:.2f}V'.format(vo_dc))

eee51.label_plot(plt_cfg, fig, ax)
plt.savefig('2N2222A_ce_transfer.pdf')


# get the gain via the slope of the transfer curve
gain_ss = np.diff(vout)/np.diff(vin)

# define the plot parameters
plt_cfg = {
        'grid_linestyle' : 'dotted',
        'title' : r'Common Emitter Amplifier Small Signal Gain',
        'xlabel' : r'$v_{in}$ [mV]',
        'ylabel' : r'Gain $A_v = \frac{\partial v_{out}}{\partial v_{in}}$',
        'legend_loc' : 'upper left',
        'add_legend' : True,
        'legend_title' : None
        }

# plot the amplifier transfer characteristics
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
ax.plot(eee51.scale_vec(vin[1:], g51.milli), gain_ss, '--', \
    label = r'$v_{OUT}$ with $R_C=$2.5 k$\Omega$')

eee51.add_vline_text(ax, 0, -50, r'$V_{BE}$ = ' + \
    '{:.1f}mV'.format(reqd_vbe/g51.milli))

eee51.add_hline_text(ax, gain_ss[index-1], -75, \
    r'$A_v=${:.2f}V'.format(gain_ss[index-1]))

ax.text(-100, -100, r'$g_m =\frac{I_C}{n\cdot V_T}=$' + \
    '{:.2f} mS'.format(gm_calc/g51.milli))

ax.text(-100, -110, r'$a_v=-g_m \cdot (R_c||r_o)=${:.2f}'.format(gain_calc))

eee51.label_plot(plt_cfg, fig, ax)
plt.savefig('2N2222A_ce_gain.pdf')


