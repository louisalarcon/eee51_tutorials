#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 10 19:50:06 2020

@author: louis
"""

import matplotlib.pyplot as plt
import numpy as np
from scipy import optimize
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

# diff amp bias points
def f1(Vbe, bjt, Ic, Vcc):
    Ic5 = (2 * Ic / bjt['beta_1mA'])
    vbe5 = bjt['n'] * g51.VT * np.log( Ic5 / \
        (bjt['Is'] * (1 + ((Vcc - Vbe)/abs(bjt['VA'])))))
    
    vce = Vbe + vbe5
    
    vbe3 = bjt['n'] * g51.VT * np.log(Ic / \
        (bjt['Is'] * ( 1 + (vce/abs(bjt['VA']))))) 
    
    return vbe3 - Vbe

Vcc = 5.0
Ic3 = 1e-3
f1_args = (pnp_2n3906, Ic3, Vcc)
Vbe3 = optimize.root(f1, 0.6, args=f1_args).x[0]

Ic5 = 2 * Ic3 / pnp_2n3906['beta_1mA']
Vce5 = Vcc - Vbe3
Vbe5 = eee51.bjt_find_vbe(Ic5, Vce5, \
    pnp_2n3906['Is'], pnp_2n3906['n'], pnp_2n3906['VA'])

Vce3 = Vbe3 + Vbe5
Vo1 = Vcc - Vce3

Ic1 = 1e-3
Vic = 1.8

def f1b(Vx, Ic1, Vo1, Vic, bjt):
    Vbe1 = eee51.bjt_find_vbe(Ic1, Vo1 - Vx, \
        bjt['Is'], bjt['n'], bjt['VA'])
    Vxp = Vic - Vbe1
    return Vxp - Vx

f1b_args = (Ic1, Vo1, Vic, npn_2n3904)
Vx = optimize.root(f1b, 0.6, args=f1b_args).x[0]

Ic6 = 2e-3
Re6 = 100

Vce6 = Vx - Ic6 * Re6
Vbe6 = eee51.bjt_find_vbe(Ic6, Vce6, \
    npn_2n3904['Is'], npn_2n3904['n'], npn_2n3904['VA'])

Ic8 = 2 * Ic6 / npn_2n3904['beta_1mA']
Vbe8 = eee51.bjt_find_vbe(Ic8, Vcc - Vbe6 - (Re6 * Ic6), \
    npn_2n3904['Is'], npn_2n3904['n'], npn_2n3904['VA'])

Vc7 = Vbe8 + Vbe6 + (Re6 * Ic6)
Rmdiff = ( Vcc - Vc7 ) / Ic6

gm1d = Ic1 / (g51.VT * npn_2n3904['n'])
ro2d = abs(npn_2n3904['VA']) / Ic1
ro4d = abs(pnp_2n3906['VA']) / Ic1

adm = gm1d * eee51.r_parallel([ro2d, ro4d])
Rod = eee51.r_parallel([ro2d, ro4d])

# CE amplifier bias
def f2(Re1, Ic1, Vo1, Vcc, bjt):    
    Vbe1 = eee51.bjt_find_vbe(Ic1, Vcc - (Re1 * Ic1) - (Vcc/2), \
        bjt['Is'], bjt['n'], bjt['VA'])
    
    Re = ( Vcc - (Vo1 + Vbe1) ) / Ic1
    
    return Re - Re1

Ic1 = 1e-3
f2_args = (Ic1, Vo1, Vcc, pnp_2n3906)
Re1 = optimize.root(f2, 600, args=f2_args).x[0]
    
gm1 = Ic1 / (g51.VT * pnp_2n3906['n'])
ro1 = abs(pnp_2n3906['VA']) / Ic1

Ic2 = 1e-3
gm2 = Ic2 / (g51.VT * npn_2n3904['n'])
ro2 = abs(npn_2n3904['VA']) / Ic2

Re2 = (ro1 - ro2 + (gm1 * ro1 * Re1))/ (gm2 * ro2)

Vbe2 = eee51.bjt_find_vbe(Ic2, (Vcc/2) - (Re2 * Ic2), \
    npn_2n3904['Is'], npn_2n3904['n'], npn_2n3904['VA'])

Vbe4 = eee51.bjt_find_vbe( 2 * ( Ic2 / npn_2n3904['beta_1mA']), \
    Vcc - Vbe2 - (Ic2 * Re2), \
    npn_2n3904['Is'], npn_2n3904['n'], npn_2n3904['VA'])

Rmce = (Vcc - Vbe2 - Vbe4 - (Re2 * Ic2)) / Ic2
Gm = gm1 / (1 + (gm1 * Re1))
av = -Gm * eee51.r_parallel([Re1 * (1 + (gm1 * ro1)) , Re2 * (1 + (gm2 * ro2)) ])
Roce = eee51.r_parallel([Re1 * (1 + (gm1 * ro1)) , Re2 * (1 + (gm2 * ro2)) ])

rpi1 = pnp_2n3906['beta_1mA'] / gm1
Rice = rpi1 * (1 + (gm1 * ro1)) 

# common collector
Vo3 = 1.8
Ic2cc = 1e-3

Vbe2cc = eee51.bjt_find_vbe(Ic2cc, Vo3, \
    npn_2n3904['Is'], npn_2n3904['n'], npn_2n3904['VA'])

Vbe4cc = eee51.bjt_find_vbe(2 * Ic2cc / npn_2n3904['beta_1mA'], Vo3, \
    npn_2n3904['Is'], npn_2n3904['n'], npn_2n3904['VA'])

Rmcc = ( Vcc - Vbe4cc - Vbe2cc ) / Ic2cc

gm1cc = Ic2cc / (g51.VT * npn_2n3904['n'])
rpi1cc = npn_2n3904['beta_1mA'] / gm1cc
ro1cc = abs(npn_2n3904['VA']) / Ic2cc

ro2cc = abs(npn_2n3904['VA']) / Ic2cc

Rocc = eee51.r_parallel([1/gm1cc, rpi1cc, ro1cc, ro2cc])
avcc = gm1cc * Rocc 
Ricc = rpi1cc * (1 + (gm1cc * ro2cc))

# run ngspice
cfg = {
        'spice' : '/Applications/ngspice/bin/ngspice', 
        'cir_dir' : '/Users/louis/Documents/UPEEEI/Classes/EEE 51/Mini Projects/',
        'cir_file' : 'opamp1.sp',
        'transfer_sim' : 'opamp1_vic=1.8_sim.dat',
        'transient_sim' : 'opamp1_tran_vic=1.8_sim.dat'
        }

# note: you can do this from the command line and just process the data files
# this was done here for convenience
eee51.run_spice(cfg)

vid = []
vo1 = []
vo2 = []
vo3 = []

with open(cfg['transfer_sim'], 'r') as f:
    for line in f:
        vid.append(float(line.split()[0]))
        vo1.append(float(line.split()[1]))
        vo2.append(float(line.split()[3]))
        vo3.append(float(line.split()[5]))

index, vin_sim = eee51.find_in_data(vid, 0.0)
indexp, vin_simp = eee51.find_in_data(vid, 100e-6)
indexn, vin_simn = eee51.find_in_data(vid, -100e-6)

# define the plot parameters
plt_cfg = {
        'grid_linestyle' : 'dotted',
        'title' : r'3-Stage Op-Amp DC Transfer Curve',
        'xlabel' : r'$v_{id}$ [$\mu$V]',
        'ylabel' : r'Voltage [V]',
        'legend_loc' : 'lower left',
        'add_legend' : True,
        'legend_title' : None
        }

fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
ax.plot(eee51.scale_vec(vid, g51.micro), vo1, '-', \
    label = r'$v_{o1}$')
ax.plot(eee51.scale_vec(vid, g51.micro), vo2, '-', \
    label = r'$v_{o2}$')
ax.plot(eee51.scale_vec(vid, g51.micro), vo3, '-', \
    label = r'$v_{o3}$')

eee51.add_vline_text(ax, 0, 0, \
    '{:.2f}V'.format(0))

eee51.add_hline_text(ax, vo1[index], -750, \
        r'{:.3f}V'.format(vo1[index]))
eee51.add_hline_text(ax, vo2[index], -750, \
        r'{:.3f}V'.format(vo2[index]))
eee51.add_hline_text(ax, vo3[index], -750, \
        r'{:.3f}V'.format(vo3[index]))

eee51.label_plot(plt_cfg, fig, ax)
plt.savefig('opamp1_transfer.png')

# define the plot parameters
plt_cfg = {
        'grid_linestyle' : 'dotted',
        'title' : r'3-Stage Op-Amp DC Transfer Curve',
        'xlabel' : r'$v_{id}$ [$\mu$V]',
        'ylabel' : r'$v_{o3}$ [V]',
        'legend_loc' : 'upper right',
        'add_legend' : True,
        'legend_title' : None
        }

fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)

ax.plot(eee51.scale_vec(vid, g51.micro), vo3, '-', \
    label = r'$v_{o3}$')

eee51.add_vline_text(ax, 0, 0.75, \
    '{:.0f}V'.format(0))
eee51.add_vline_text(ax, vid[indexp]/g51.micro, 2, \
    '{:.0f}'.format(vid[indexp]/g51.micro) + r'$\mu$V')
eee51.add_vline_text(ax, vid[indexn]/g51.micro, 2, \
    '{:.0f}'.format(vid[indexn]/g51.micro)  + r'$\mu$V')

eee51.add_hline_text(ax, vo3[index], -750, \
        r'{:.3f}V'.format(vo3[index]))
eee51.add_hline_text(ax, vo3[indexp], -750, \
        r'{:.3f}V'.format(vo3[indexp]))
eee51.add_hline_text(ax, vo3[indexn], -750, \
        r'{:.3f}V'.format(vo3[indexn]))

eee51.label_plot(plt_cfg, fig, ax)
plt.savefig('opamp1_transfer_swing.png')

# read in transient simulation data
t = []
vid = []
vo3 = []

with open(cfg['transient_sim'], 'r') as f:
    for line in f:
        t.append(float(line.split()[0]))
        vid.append(float(line.split()[1]))
        vo3.append(float(line.split()[7]))

vidpp = max(vid) - min(vid)
vo3pp = max(vo3) - min(vo3)

# define the plot parameters
plt_cfg = {
        'grid_linestyle' : 'dotted',
        'title' : r'3-Stage Op-Amp Transient Response',
        'xlabel' : r'Time [ms]',
        'ylabel' : r'$v_{o3}$ [V]',
        'legend_loc' : 'upper left',
        'add_legend' : True,
        'legend_title' : None
        }

fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
ax2 = ax.twinx()

ax2.plot(eee51.scale_vec(t, g51.milli), eee51.scale_vec(vid, g51.micro), '--', \
    label = r'$v_{id}$ = ' + '{:.2f} '.format(vidpp/g51.micro) + r'$\mu V_{p-p}$')

ax.plot(eee51.scale_vec(t, g51.milli), vo3, '-', color = 'orangered', \
    label = r'$v_{o3}$ = ' + '{:.2f} '.format(vo3pp) + r'$V_{p-p}$')

ax2.set_ylabel(r'$v_{id}$ [mV]')
ax2.legend(loc='upper right')

ax.set_ylim(-2, 4)
ax2.set_ylim(-210, 810)

eee51.label_plot(plt_cfg, fig, ax)
plt.savefig('opamp1_transient_zoom.png')
