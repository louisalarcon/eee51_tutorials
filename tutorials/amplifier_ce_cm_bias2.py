#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 18 12:07:00 2020

@author: louis
"""

import matplotlib.pyplot as plt
import numpy as np
import eee51, g51 
from si_prefix import si_format
from statistics import mean


# load constants
g51.init_global_constants()

# ideal BJT parameters
pnp_2n3906 = {
        'Is' : 1.2578290761605683e-13,
        'n' : 1.198768650455792,
        'VA' : -6.889646437848553,
        'beta_1mA' : 241.53404979129192
        }

npn_2n3904 = {
        'Is' : 8.551790244629221e-12,
        'n' : 1.4032493041038172,
        'VA' : -6.567733723930889,
        'beta_1mA' : 135.63663029082588
        }

# Let's calculate the resistor needed to set the 
# output of the pnp current mirror to 1mA at a 2.5V output 
specs = {
        'ic' : 1e-3,
        'vce' : 2.5,
        'vcc' : 5.0
        }

vbe23 = eee51.bjt_find_vbe( \
        specs['ic'], \
        specs['vce'], pnp_2n3906['Is'], \
        pnp_2n3906['n'], pnp_2n3906['VA'])

# since we want to vce2 = 2.5V, and vce3 = vbe3 = vbe2 approx 0.7, we can use
# VA to derate the ic of Q2:

# ic3 / ic2 = ( 1 + vce3/va ) / (1 + vce2/va)

ic3 = specs['ic'] * (1 + (vbe23/abs(pnp_2n3906['VA']))) / \
    (1 + (specs['vce']/abs(pnp_2n3906['VA'])))

ib3 = ic3 / pnp_2n3906['beta_1mA']
ib2 = specs['ic'] / pnp_2n3906['beta_1mA']

iR = ic3 + ib3 + ib2
Rbias = ( specs['vcc'] - vbe23 ) / iR

# let's bias Q1 with a diode-connected npn as well

vbe14 = eee51.bjt_find_vbe( \
        specs['ic'], \
        specs['vce'], npn_2n3904['Is'], \
        npn_2n3904['n'], npn_2n3904['VA'])

ic4 = specs['ic'] * (1 + (vbe14/abs(npn_2n3904['VA']))) / \
    (1 + (specs['vce']/abs(npn_2n3904['VA'])))

ib4 = ic4 / npn_2n3904['beta_1mA']
ib1 = specs['ic'] / npn_2n3904['beta_1mA']

iR2 = ic4 + ib4 + ib1
Rbias2 = ( specs['vcc'] - vbe14 ) / iR2

vbe1_used = vbe14

# run ngspice
cfg = {
        'spice' : '/Applications/ngspice/bin/ngspice', 
        'cir_dir' : '/Users/louis/Documents/UPEEEI/Classes/EEE 51/Mini Projects/',
        'cir_file' : 'amplifier_CE_CM_bias2.sp',
        'transfer_data' : 'amp_ce_cm2_transfer_sim.dat',
        'transient_data' : 'amp_ce_cm2_transient_sim.dat'
        }

# note: you can do this from the command line and just process the data files
# this was done here for convenience
eee51.run_spice(cfg)

# open the transfer characteristics data file and get the data
vin = []    # declare list for vin
vout = []   # declare a list for vout
ic1 = []     # declare a list for ic1

with open(cfg['transfer_data'], 'r') as f:
    for line in f:
        vin.append(float(line.split()[0]))
        vout.append(float(line.split()[1]))
        ic1.append(float(line.split()[3]))
        

#g51.update_bjt_VA(-15.550605626760145) 

index, vin_sim = eee51.find_in_data(vin, 0.0)
vo_dc = vout[index]


# define the plot parameters
plt_cfg = {
        'grid_linestyle' : 'dotted',
        'title' : r'Common Emitter CM Bias DC Transfer Curve',
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
    label = r'$v_{OUT}$')

ax2 = ax.twinx()
ax2.set_ylabel(r'$I_C$ [mA]')
ax2.plot(eee51.scale_vec(vin, g51.milli), eee51.scale_vec(ic1, g51.milli), \
         ':', color='orangered', label = r'$I_C$')
ax2.legend(loc='upper right')


eee51.add_vline_text(ax, 0, 0, r'$V_{IN}$ = ' + \
    '{:.1f}mV'.format(0))

eee51.add_vline_text(ax, 10, 0, r'$V_{IN}$ = ' + \
    '{:.1f}mV'.format(10))

eee51.add_vline_text(ax, -10, 0, r'$V_{IN}$ = ' + \
    '{:.1f}mV'.format(-10))

eee51.add_hline_text(ax, vo_dc, -75, \
    r'$V_{OUT}=$' + '{:.2f}V'.format(vo_dc))

eee51.add_hline_text(ax2, ic1[index]/g51.milli, 50, \
    r'$I_C=$' + '{:.2f}mA'.format(ic1[index]/g51.milli))

eee51.label_plot(plt_cfg, fig, ax)
plt.savefig('amp_ce_cm2_transfer.png')


# get the gain via the slope of the transfer curve
gain_ss = np.diff(vout)/np.diff(vin)

ro1_calc = abs(npn_2n3904['VA']) / ic1[index] 
ro2_calc = abs(pnp_2n3906['VA']) / ic1[index] 


gm1_calc = ic1[index]/(npn_2n3904['n'] * g51.VT)
gain_calc = -gm1_calc * eee51.r_parallel([ro1_calc, ro2_calc])

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
    label = r'$A_v$')

#eee51.add_vline_text(ax, 0, -80, r'$V_{BE}$ = ' + \
#    '{:.1f}mV'.format(vbe1_used/g51.milli))

eee51.add_hline_text(ax, gain_ss[index-1], -75, \
    r'$A_v=${:.2f}V'.format(gain_ss[index-1]))

ax.text(-100, -65, r'$r_{o1} =\frac{V_{A1}}{I_C}=$' + \
    si_format(ro1_calc, precision=2) + '$\Omega$')

ax.text(-100, -80, r'$r_{o2} =\frac{V_{A2}}{I_C}=$' + \
    si_format(ro2_calc, precision=2) + '$\Omega$')

ax.text(-100, -95, r'$g_{m1} =\frac{I_{C1}}{n_1\cdot V_T}=$' + \
    '{:.2f} mS'.format(gm1_calc/g51.milli))

ax.text(-100, -110, r'$a_v=-g_{m1} \cdot (r_{o1}||r_{o2})=$' + \
    '{:.2f}'.format(gain_calc))

eee51.label_plot(plt_cfg, fig, ax)
plt.savefig('amp_ce_cm2_gain.png')

# open the transfer characteristics data file and get the data
t = []   # declare list for the time variable
vin = []    # declare list for vin
vout = []   # declare a list for vout

with open(cfg['transient_data'], 'r') as f:
    for line in f:
        t.append(float(line.split()[0]))
        vin.append(float(line.split()[3]))
        vout.append(float(line.split()[1]))
        
vinpp = max(vin) - min(vin)
voutpp = max(vout) - min(vout)
vout_dc = mean(vout)
vin_dc = mean(vin)

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

# plot the amplifier transient characteristics
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
ax2.set_ylim(650, 850)


eee51.add_hline_text(ax2, vin_dc/g51.milli, 3.75, \
    r'$V_{IN}=$' + '{:.2f}mV'.format(vin_dc/g51.milli))

eee51.add_hline_text(ax, vout_dc, 0, \
    r'$V_{OUT}=$' + '{:.2f}V'.format(vout_dc))

ax.text(0, 4, r'$a_v=\frac{V_{OUT,p-p}}{V_{IN,p-p}}=$' + \
    '{:.2f}'.format(voutpp/vinpp))

eee51.label_plot(plt_cfg, fig, ax)
plt.savefig('amp_ce_cm2_transient_zoom.png')
