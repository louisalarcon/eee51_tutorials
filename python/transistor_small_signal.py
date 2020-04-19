#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 15:34:50 2020

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

# open the transfer characteristics data file and get the data
vbe = []    # declare list for vbe
ic = []     # declare a list for ic with vce = vce,sat = 0.2V
ic2 = []    # declare a list for ic with vce = 2.5V
ib2 = []    # declare a list for ib with vce = 2.5V
            
with open(cfg['transfer_data'], 'r') as f:
    for line in f:
        vbe.append(float(line.split()[0]))
        ic.append(float(line.split()[1]))
        ic2.append(float(line.split()[3]))
        ib2.append(float(line.split()[5]))

# convert to mV and mA
ic_mA = eee51.scale_vec(ic, g51.milli)
vbe_mV = eee51.scale_vec(vbe, g51.milli)

bjt_beta = [a/b for a, b in zip(ic2, ib2)]

# bjt parameters from our dc characterization
bjt_Is = 6.924988420125876e-13
bjt_n = 1.2610858394025979
g51.update_bjt_VA(-15.550605626760145) 
g51.update_bjt_vce(specs['vce'])     
    

# calculate the vbe needed for vce = 2.5V
reqd_vbe = eee51.bjt_find_vbe(specs['ic'], specs['vce'], \
        bjt_Is, bjt_n, g51.bjt_VA)

# generate the ic for the ideal bjt model 
# using our values for Is, n, and VA at vce = 2.5V

ic_ideal = [eee51.ideal_bjt_transfer(v, bjt_Is, bjt_n) for v in vbe]
ic_ideal_mA = eee51.scale_vec(ic_ideal, g51.milli)

# define the plot parameters
plt_cfg = {
        'grid_linestyle' : 'dotted',
        'title' : 'BJT 2N2222A Transfer Characteristics',
        'xlabel' : r'$V_{BE}$ [V]',
        'ylabel' : r'$I_C$ [mA]',
        'legend_loc' : 'upper left',
        'add_legend' : True,
        'legend_title' : None
        }

# plot the transfer characteristics at 2.5V
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
ax.plot(vbe_mV, eee51.scale_vec(ic2, g51.milli), '--', \
    label = 'simulation ($V_{CE}$=2.5V)')
ax.plot(vbe_mV, ic_ideal_mA, \
    label = 'ideal BJT using $I_S$=' + \
    si_format(bjt_Is, precision=2) + r'A, $n$={:.2f}, and '.format(bjt_n) + \
    r'$|V_A|$={:.2f}'.format(abs(g51.bjt_VA)))

eee51.add_vline_text(ax, reqd_vbe/g51.milli, 2.5, '$V_{BE}$ = ' + \
    '{:.1f}mV'.format(reqd_vbe/g51.milli))

eee51.add_hline_text(ax, specs['ic']/g51.milli, 550, \
    '$I_C$ = {:.1f}mA'.format(specs['ic']/g51.milli))

eee51.label_plot(plt_cfg, fig, ax)

# get the derivative of ic with respect to vbe
dic2 = np.diff(ic2)/np.diff(vbe)
dic_ideal = np.diff(ic_ideal)/np.diff(vbe)

index, vbe_sim = eee51.find_in_data(vbe, reqd_vbe)
gm_sim = dic2[index-1]
gm_ideal = dic_ideal[index-1]

# calculate the bjt small signal parameters
gm_calc = ic2[index]/(bjt_n * g51.VT)

ro_calc = abs(g51.bjt_VA) / ic2[index] 
rpi_calc = bjt_beta[index] / gm_calc

ao_calc = gm_calc * ro_calc

# define the plot parameters
plt_cfg = {
        'grid_linestyle' : 'dotted',
        'title' : r'BJT 2N2222A ${\partial I_C}/{\partial V_{BE}}$',
        'xlabel' : r'$V_{BE}$ [V]',
        'ylabel' : r'${\partial I_C}/{\partial V_{BE}}$ [mS]',
        'legend_loc' : 'upper left',
        'add_legend' : True,
        'legend_title' : None
        }

# plot the derivative of transfer characteristics at 2.5V
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
ax.plot(vbe_mV[1:], eee51.scale_vec(dic2, g51.milli), '--', \
    label = 'simulation ($V_{CE}$=2.5V)')
ax.plot(vbe_mV[1:], eee51.scale_vec(dic_ideal, g51.milli), \
    label = 'ideal BJT using $I_S$=' + \
    si_format(bjt_Is, precision=2) + r'A, $n$={:.2f}, and '.format(bjt_n) + \
    r'$|V_A|$={:.2f}V'.format(abs(g51.bjt_VA)))

eee51.add_vline_text(ax, reqd_vbe/g51.milli, 75, r'$V_{BE}$ = ' + \
    '{:.1f}mV'.format(reqd_vbe/g51.milli))

eee51.add_hline_text(ax, gm_sim/g51.milli, 600, \
    r'$g_m$ = {:.2f}mS (sim)'.format(gm_sim/g51.milli))

ax.text(500, 175, r'$|V_A|$={:.2f}V, '.format(abs(g51.bjt_VA)) + \
        r'$\beta_{DC}=$' + '{:.2f}'.format(bjt_beta[index]) )
ax.text(500, 150, r'$g_{m,ideal}$' + '={:.2f} mS'.format(gm_ideal/g51.milli))

ax.text(500, 125, r'$g_m=\frac{I_C}{n \cdot V_T}=$' + \
        '{:.2f} mS'.format(gm_calc/g51.milli))

ax.text(500, 100, r'$r_o=\frac{|V_A|}{I_C}=$' + \
        si_format(ro_calc, precision=2) + '$\Omega$')

ax.text(580, 100, r'$r_\pi=\frac{\beta_{DC}}{g_m}=$' + \
        si_format(rpi_calc, precision=2) + '$\Omega$')

ax.text(500, 75, r'$a_o=|g_m \cdot r_o|=${:.2f}'.format(ao_calc))

eee51.label_plot(plt_cfg, fig, ax)
plt.savefig('2N2222A_small_signal_2500mV.pdf')
