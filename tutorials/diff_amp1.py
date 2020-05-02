#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 26 13:02:54 2020

@author: louis
"""

import matplotlib.pyplot as plt
import numpy as np
import eee51, g51 

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

specs = {
        'ic1' : 1e-3,   # 1mA for ic1 and ic2, 2mA tail current
        'vxmin' : 0.5,
        'vomin' : 2.0,
        'swingpp' : 3.0,
        'vcc' : 5.0
        }

itail = 2 * specs['ic1']
vout = ( ( specs['vcc'] - specs['vomin'] ) / 2 ) + specs['vomin']

Rload = ( specs['vcc'] - specs['vomin'] ) / itail 

# common mode input range
cmir = vout - (specs['swingpp']/2) - 0.2 - specs['vxmin']   # vicmax - vicmin
vxbias = specs['vxmin'] + (cmir/2)

# bias in the middle of the cmir
vbe34 = eee51.bjt_find_vbe( \
        itail, \
        vxbias, npn_2n3904['Is'], \
        npn_2n3904['n'], npn_2n3904['VA'])

ib3 = itail / npn_2n3904['beta_1mA']

ic4 = itail
ib4 = ic4 / npn_2n3904['beta_1mA']

Re = [0, 50, 100]
Rm = [( specs['vcc'] - vbe34 - (R * ic4) ) / ( ic4 + ib3 + ib4) \
      for R in Re]

vbe12 = eee51.bjt_find_vbe( \
        specs['ic1'], \
        vout - vxbias, npn_2n3904['Is'], \
        npn_2n3904['n'], npn_2n3904['VA'])

vicmin = vbe12 + specs['vxmin']
vicmax = vout - (specs['swingpp']/2) - 0.2 + vbe12

vicbias = vbe12 + vxbias

# run ngspice
cfg = {
        'spice' : '/Applications/ngspice/bin/ngspice', 
        'cir_dir' : '/Users/louis/Documents/UPEEEI/Classes/EEE 51/Mini Projects/',
        'cir_file' : 'diff_amp1.sp',
        'transfer_vic=1.2' : 'diff_amp1_vic=1.2_Re=100_sim.dat',
        'transfer_vic=1.8' : 'diff_amp1_vic=1.8_Re=100_sim.dat',
        'transfer_vic=2.4' : 'diff_amp1_vic=2.4_Re=100_sim.dat',
        'transient_vic=1.8' : 'diff_amp1_transient_Re=100_sim.dat',
        'vcm_sweep_Re=0' : 'diff_amp1_vcm_Re=0_sim.dat',
        'vcm_sweep_Re=50' : 'diff_amp1_vcm_Re=50_sim.dat',
        'vcm_sweep_Re=100' : 'diff_amp1_vcm_Re=100_sim.dat'
        }

# note: you can do this from the command line and just process the data files
# this was done here for convenience
eee51.run_spice(cfg)

# open the common-mode transfer characteristics data file and get the data
cm_files = [cfg['vcm_sweep_Re=0'], \
            cfg['vcm_sweep_Re=50'], \
            cfg['vcm_sweep_Re=100']]

cm_labels = [r'$R_E=0\Omega$', r'$R_E=50\Omega$', r'$R_E=100\Omega$']

# define the plot parameters
plt_cfg = {
        'grid_linestyle' : 'dotted',
        'title' : r'Tail Current Common-Mode Characteristics',
        'xlabel' : r'$V_{ic}$ [V]',
        'ylabel' : r'$I_{tail}$ [mA]',
        'legend_loc' : 'lower right',
        'add_legend' : True,
        'legend_title' : 'Degeneration'
        }

# plot the common mode characteristics
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)

for cm_file, cm_label in zip(cm_files, cm_labels):
    vcm = []
    itail = []
    vop = []

    with open(cm_file, 'r') as f:
        for line in f:
            vcm.append(float(line.split()[0]))
            itail.append(float(line.split()[1]))
            vop.append(float(line.split()[3]))

    ax.plot(vcm, eee51.scale_vec(itail, g51.milli), '-', \
            label = cm_label)

eee51.add_vline_text(ax, vicmin, 0, r'$V_{ic,\min}$ = ' + \
    '{:.3f}'.format(vicmin))
eee51.add_vline_text(ax, vicmax, 0, r'$V_{ic,\max}$ = ' + \
    '{:.3f}'.format(vicmax))

eee51.label_plot(plt_cfg, fig, ax)
plt.savefig('diff_amp1_vcm_itail.png')

dm_files = [cfg['transfer_vic=1.2'], \
            cfg['transfer_vic=1.8'], \
            cfg['transfer_vic=2.4']]

vic_values = [1.2, 1.8, 2.4]
vod_values = [[], [], []]

for dm_file, vic_value, vod_value in zip(dm_files, vic_values, vod_values):
    # plot the differential mode characteristics
    vid = []
    von = []
    vop = []
    vx = []
    ic1 = []
    ic2 = []
    itail = []

    with open(dm_file, 'r') as f:
        for line in f:
            vid.append(float(line.split()[0]))
            vop.append(float(line.split()[1]))
            von.append(float(line.split()[3]))
            vx.append(float(line.split()[5]))
            ic1.append(float(line.split()[7]))
            ic2.append(float(line.split()[9]))
            itail.append(float(line.split()[11]))

    index, val = eee51.find_in_data(vid, 0)

    # define the plot parameters
    plt_cfg = {
        'grid_linestyle' : 'dotted',
        'title' : r'Differential Amplifier ($V_{IC}=$' + \
            '{:.1f}V)'.format(vic_value),
        'xlabel' : r'$V_{id}$ [mV]',
        'ylabel' : r'Voltage [V]',
        'legend_loc' : 'upper right',
        'add_legend' : False,
        'legend_title' : None
        }

    # plot the amplifier transfer characteristics
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.plot(eee51.scale_vec(vid, g51.milli), vop, '-', \
        label = r'$V_{o,p}$')
    ax.plot(eee51.scale_vec(vid, g51.milli), von, '-', \
        label = r'$V_{o,n}$')
    ax.plot(eee51.scale_vec(vid, g51.milli), vx, '-', \
        label = r'$V_x$')

    ax.set_ylim(0, 6)
    ax.legend(ncol=3)

    eee51.add_vline_text(ax, 0, 4, r'$V_{id}$ = ' + \
        '{:.1f}'.format(0.0))

    eee51.add_hline_text(ax, von[index], -200, \
        r'{:.2f}V'.format(von[index]))

    eee51.add_hline_text(ax, vx[index], -200, \
        r'{:.2f}V'.format(vx[index]))

    eee51.label_plot(plt_cfg, fig, ax)
    plt.savefig('diff_amp1_vdm_vic={:.1f}.png'.format(vic_value))

    vod = [x - y for x, y in zip(vop, von)]
    vod_value.append(vod)
    
    # define the plot parameters
    plt_cfg = {
        'grid_linestyle' : 'dotted',
        'title' : r'Differential Amplifier ' + \
            '($V_{IC}=$' + '{:.1f}V)'.format(vic_value),
        'xlabel' : r'$V_{id}$ [mV]',
        'ylabel' : r'Current [mA]',
        'legend_loc' : 'upper right',
        'add_legend' : False,
        'legend_title' : None
        }

    # plot the amplifier transfer characteristics
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.plot(eee51.scale_vec(vid, g51.milli), eee51.scale_vec(ic1, g51.milli), '-', \
        label = r'$I_{C1}$')
    ax.plot(eee51.scale_vec(vid, g51.milli), eee51.scale_vec(ic2, g51.milli), '-', \
        label = r'$I_{C2}$')
    ax.plot(eee51.scale_vec(vid, g51.milli), \
        eee51.scale_vec(itail, g51.milli), '-', \
        label = r'$I_{tail}$')

    ax.set_ylim(-0.2, 2.5)
    ax.legend(ncol=3)

    eee51.add_vline_text(ax, 0, 0, r'$V_{id}$ = ' + \
        '{:.1f}'.format(0.0))

    eee51.add_hline_text(ax, ic1[index]/g51.milli, -200, \
        r'{:.2f}mA'.format(ic1[index]/g51.milli))

    eee51.add_hline_text(ax, itail[index]/g51.milli, -200, \
        r'$I_{tail}=$' + r'{:.2f}mA'.format(itail[index]/g51.milli))


    eee51.label_plot(plt_cfg, fig, ax)
    plt.savefig('diff_amp1_currents_vic={:.1f}.png'.format(vic_value))
    
# define the plot parameters
plt_cfg = {
        'grid_linestyle' : 'dotted',
        'title' : r'Differential Amplifier Transfer Characteristics',
        'xlabel' : r'$V_{id}$ [mV]',
        'ylabel' : r'$V_{od}$ [V]',
        'legend_loc' : 'upper right',
        'add_legend' : True,
        'legend_title' : None
        }

# plot the amplifier transfer characteristics
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)

for vod_value, vic_value in zip(vod_values, vic_values):
    ax.plot(eee51.scale_vec(vid, g51.milli), vod, '-', \
        label = r'$V_{IC}=$' + '{:.1f}V'.format(vic_value))

eee51.add_vline_text(ax, 0, -2.5, r'$V_{id}$ = ' + \
    '{:.1f}'.format(0.0))

eee51.label_plot(plt_cfg, fig, ax)
plt.savefig('diff_amp1_transfer_sim.png')

gain_values = [[], [], []]
for vod_value, gain_value in zip(vod_values, gain_values):
    # get the gain via the slope of the transfer curve
    gain_ss = np.diff(vod_value)/np.diff(vid)
    gain_value.append(gain_ss)
    
gm1 = specs['ic1'] / g51.VT
ro1 = abs(npn_2n3904['VA']) / specs['ic1']
RL = 1.5e3

gain_calc = -gm1 * eee51.r_parallel([ro1, RL])

index, val = eee51.find_in_data(vid, 0)

# define the plot parameters
plt_cfg = {
        'grid_linestyle' : 'dotted',
        'title' : r'Small Signal Differential Gain',
        'xlabel' : r'$V_{id}$ [mV]',
        'ylabel' : r'Gain $A_{dm} = \frac{\partial v_{od}}{\partial v_{id}}$',
        'legend_loc' : 'upper right',
        'add_legend' : True,
        'legend_title' : None
        }

# plot the amplifier transfer characteristics
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)

for gain_value, vic_value in zip(gain_values, vic_values):
    ax.plot(eee51.scale_vec(vid[1:], g51.milli), gain_value[0][0], '-', \
        label = r'$V_{IC}=$' + '{:.1f}V'.format(vic_value))


eee51.add_vline_text(ax, 0, -20, r'$V_{id}$ = ' + \
    '{:.1f}'.format(0.0))

ax.text(-200, -30, r'$A_{dm}=-g_{m1} \cdot (r_{o1}||R_L)$')
ax.text(-177, -33, r'$=$' + '{:.2f}'.format(gain_calc))

eee51.add_hline_text(ax, gain_values[1][0][0][index], -200, \
    r'{:.2f}V'.format(gain_values[1][0][0][index]))

eee51.label_plot(plt_cfg, fig, ax)
plt.savefig('diff_amp1_gain_sim.png')

# read in transient simulation data
t = []
vop = []
von = []
vip = []
vin = []
vx = []
ic1 = []
ic2 = []
itail = []

with open(cfg['transient_vic=1.8'], 'r') as f:
    for line in f:
        t.append(float(line.split()[0]))
        vop.append(float(line.split()[1]))
        von.append(float(line.split()[3]))
        vip.append(float(line.split()[5]))
        vin.append(float(line.split()[7]))
        vx.append(float(line.split()[9]))
        ic1.append(float(line.split()[11]))
        ic2.append(float(line.split()[13]))
        itail.append(float(line.split()[15]))

vod = [x - y for x, y in zip(vop, von)]
vid = [x - y for x, y in zip(vip, vin)]

vidpp = max(vid) - min(vid)
vodpp = max(vod) - min(vod)

# define the plot parameters
plt_cfg = {
        'grid_linestyle' : 'dotted',
        'title' : r'Transient Response ($V_{ic}=1.8V$)',
        'xlabel' : r'Time [ms]',
        'ylabel' : r'$v_{od}$ [V]',
        'legend_loc' : 'upper left',
        'add_legend' : True,
        'legend_title' : None
        }

# plot the amplifier transient characteristics
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
ax2 = ax.twinx()

ax2.plot(eee51.scale_vec(t, g51.milli), eee51.scale_vec(vid, g51.milli), '--', \
    label = r'$v_{id}$ = ' + '{:.2f} '.format(vidpp/g51.milli) + r'$mV_{p-p}$')

ax.plot(eee51.scale_vec(t, g51.milli), vod, '-', color = 'orangered', \
    label = r'$v_{od}$ = ' + '{:.2f} '.format(vodpp) + r'$V_{p-p}$')

ax2.set_ylabel(r'$v_{id}$ [mV]')
ax2.legend(loc='upper right')

ax.set_ylim(-2.2, 2.2)
ax2.set_ylim(-110, 110)

eee51.label_plot(plt_cfg, fig, ax)
plt.savefig('diff_amp1_transient_zoom.png')

