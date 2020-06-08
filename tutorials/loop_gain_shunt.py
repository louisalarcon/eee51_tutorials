#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 17 15:27:57 2020

@author: louis
"""

import matplotlib.pyplot as plt
import numpy as np
import eee51, g51 
from scipy.optimize import curve_fit
import math
from si_prefix import si_format

# load constants
g51.init_global_constants()


# run ngspice
cfg = {
        'spice' : '/Applications/ngspice/bin/ngspice', 
        'cir_dir' : '/Users/louis/Documents/UPEEEI/Classes/EEE 51/Mini Projects/',
        'cir_file' : 'loop_gain_shunt.sp',
        'ac_sim' : 'loop_gain_shunt_ac.dat',
        'tran_sim_1' : 'loop_gain_shunt_transient_1.dat'
        }

# note: you can do this from the command line and just process the data files
# this was done here for convenience
eee51.run_spice(cfg)
    
# ac analysis results

def fmag_2p1z(w, ao, wp1, wp2, wz):
    n = (1 - ((1j * w)/wz))
    d = (1 + ((1j * w)/wp1)) * (1 + ((1j * w)/wp2))
    return 20 * np.log10( np.abs( ao * n / d) )

freq = []
vo3 = []
ifb = []
ierr = []
vo1 = []
iin3 = []

with open(cfg['ac_sim'], 'r') as f:
    for line in f:
        freq.append(float(line.split()[0]))
        vo3.append(float(line.split()[1]) + (float(line.split()[2])*1j) )
        ifb.append(float(line.split()[4]) + (float(line.split()[5])*1j) )
        ierr.append(float(line.split()[7]) + (float(line.split()[8])*1j) )
        vo1.append(float(line.split()[10]) + (float(line.split()[11])*1j) )
        iin3.append(float(line.split()[13]) + (float(line.split()[14])*1j) )

vo3_mag = np.abs(vo3)
vo3_phase = np.angle(vo3, deg = True)    
        
labels = ['$f_{p1}$ = ', '$f_{p2}$ = ', '$f_z$ = ']
angles = [135, 45, -45]
guess = [1e2, 1e2, 1e6, 1e9]
freq_rad = [2 * math.pi * f for f in freq]

def TransferFunction(out_data, in_data):
    H = [x/y for x, y in zip(out_data, in_data)]
    H_mag = np.abs(H)
    H_phase = np.angle(H, deg = True)
    
    return H, H_mag, H_phase

T, T_mag, T_phase = TransferFunction(ifb, ierr)
Rm, Rm_mag, Rm_phase = TransferFunction(vo1, ierr)
F, F_mag, F_phase = TransferFunction(ifb, vo1)
Finv, Finv_mag, Finv_phase = TransferFunction(vo1, ifb)
Rcl, Rcl_mag, Rcl_pgase = TransferFunction(vo3, iin3)

popt, pcov = curve_fit(fmag_2p1z, freq_rad, \
                       20*np.log10( T_mag ), \
                       p0=guess)

To_dB_calc = 20 * np.log10( popt[0] )

index_To0dB, To0dB = eee51.find_in_data( 20*np.log10( T_mag ), 0 )
fu = freq[index_To0dB]

dTdf = np.diff(20*np.log10( T_mag ))/np.diff(np.log10(freq_rad))

PM = T_phase[index_To0dB] - (-180)

# define the plot parameters
plt_cfg = {
    'grid_linestyle' : 'dotted',
    'title' : r'Shunt Amplifier Loop Gain (PM = {:.1f} deg)'.format(PM),
    'xlabel' : r'Frequency [Hz]',
    'ylabel' : r'Magnitude [dB]',
    'legend_loc' : 'upper right',
    'add_legend' : True,
    'legend_title' : None
    }

fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
ax.set_ylim(-300, 200)

ax.semilogx(freq, 20*np.log10(Rm_mag), '-', label = r'$R_m=\frac{v_o}{i_{\epsilon}}$')
ax.semilogx(freq, 20*np.log10(Finv_mag), '-', label = r'$\frac{1}{F}$')

ax.semilogx(freq, 20*np.log10(T_mag), '-', label = '$T=R_m\cdot F$')

ax.semilogx(freq, 20*np.log10(Rcl_mag), '--', \
    label = r'$R_{m,CL}=\frac{1}{F}\cdot\frac{T}{1+T}$')

eee51.add_hline_text(ax, To_dB_calc, 1e2, \
    r'$T_0$ = {:.1f}dB'.format(To_dB_calc))

for w, label in zip(popt[1:], labels):
    eee51.add_vline_text(ax, w / (2 * math.pi ), -250, label + \
        si_format(w / (2 * math.pi ), precision=2) + 'Hz')

eee51.add_vline_text(ax, fu, -250, r'$f_u=$' + \
        si_format(fu, precision=2) + 'Hz')

eee51.label_plot(plt_cfg, fig, ax)
plt.savefig('loop_agin_shunt_mag_1.png')


# define the plot parameters
plt_cfg = {
        'grid_linestyle' : 'dotted',
        'title' : r'Shunt Amplifier Loop Gain (PM = {:.1f} deg)'.format(PM),
        'xlabel' : r'Frequency [Hz]',
        'ylabel' : r'Phase [degrees]',
        'legend_loc' : 'lower left',
        'add_legend' : False,
        'legend_title' : None
        }

fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)

ax.semilogx(freq, T_phase, '-')

for w, label in zip(popt[1:], labels):
    eee51.add_vline_text(ax, w / (2 * math.pi ), 25, label + \
        si_format(w / (2 * math.pi ), precision=2) + 'Hz')
    
eee51.add_vline_text(ax, fu, 25, r'$f_u=$' + \
        si_format(fu, precision=2) + 'Hz')

eee51.add_hline_text(ax, -180, 1e9, \
        r'{:.1f} deg'.format(-180))

eee51.add_hline_text(ax, T_phase[index_To0dB], 1e9, \
        r'{:.1f} deg'.format(T_phase[index_To0dB]))

eee51.label_plot(plt_cfg, fig, ax)
plt.savefig('loop_gain_shunt_phase_1.png')

# transient response
t = []
vo3 = []
vi3 = []

with open(cfg['tran_sim_1'], 'r') as f:
    for line in f:
        t.append(float(line.split()[0]))
        vo3.append(float(line.split()[1]))
        vi3.append(float(line.split()[3]))
     
vo3pp = si_format(max(vo3) - min(vo3), precision=2) + 'V'
vi3pp = si_format(max(vi3) - min(vi3), precision=2) + 'V'

Acl = si_format((max(vo3) - min(vo3))/(max(vi3) - min(vi3)), precision=2)
        
# define the plot parameters
plt_cfg = {
    'grid_linestyle' : 'dotted',
    'title' : r'Closed-Loop Transient Response ($|A_{v,CL}|=$' + Acl + ')',
    'xlabel' : r'Time [s]',
    'ylabel' : r'Output Voltage [v]',
    'legend_loc' : 'upper left',
    'add_legend' : True,
    'legend_title' : None
    }

fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
ax2 = ax.twinx()

ax2.set_ylabel('Input Voltage [V]')

ax.set_ylim( np.mean(vo3) - ( 2.25 * ( np.mean(vo3) - min(vo3) )), \
    np.mean(vo3) + ( 1.75 * ( max(vo3) - np.mean(vo3) )))

ax.plot(t, vo3, '-', color='red', \
        label = r'$v_{o,p-p}=$' + vo3pp)

ax2.set_ylim(-300, 1750)
ax2.plot(t, eee51.scale_vec(vi3, g51.milli), '-', \
    label = r'$v_{i,p-p}=$' + vi3pp)

ax2.legend(loc='upper right')
    
eee51.label_plot(plt_cfg, fig, ax)
plt.savefig('loop_gain_shunt_cl_tran.png')
