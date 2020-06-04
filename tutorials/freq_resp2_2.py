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
        'cir_file' : 'amplifier_CE_CM_bias2_freq.sp',
        'ac_1_sim' : 'amp_ce_cm_ac_1_sim.dat',
        'ac_2_sim' : 'amp_ce_cm_ac_2_sim.dat',
        'ac_3_sim' : 'amp_ce_cm_ac_3_sim.dat',
        'ac_4_sim' : 'amp_ce_cm_ac_4_sim.dat',
        'tran_sim_1' : 'amp_ce_cm_transient_1_sim.dat',
        'tran_sim_2' : 'amp_ce_cm_transient_2_sim.dat',
        'tran_sim_3' : 'amp_ce_cm_transient_3_sim.dat'
        }

# note: you can do this from the command line and just process the data files
# this was done here for convenience
eee51.run_spice(cfg)
    
# ac analysis results

ac_files = [cfg['ac_1_sim'], cfg['ac_2_sim'], \
            cfg['ac_3_sim'], cfg['ac_4_sim']]

output_mag_files = ['amp_ce_cm_ac_1_mag.png', 'amp_ce_cm_ac_2_mag.png', \
                    'amp_ce_cm_ac_3_mag.png', 'amp_ce_cm_ac_4_mag.png' ]

output_slope_files = ['amp_ce_cm_ac_1_slope.png', 'amp_ce_cm_ac_2_slope.png', \
                    'amp_ce_cm_ac_3_slope.png', 'amp_ce_cm_ac_4_slope.png' ]

output_phase_files = ['amp_ce_cm_ac_1_phase.png', \
                      'amp_ce_cm_ac_2_phase.png', \
                      'amp_ce_cm_ac_3_phase.png', \
                      'amp_ce_cm_ac_4_phase.png']

def fmag_2p1z(w, ao, wp1, wp2, wz):
    n = (1 - ((1j * w)/wz))
    d = (1 + ((1j * w)/wp1)) * (1 + ((1j * w)/wp2))
    return 20 * np.log10( np.abs( ao * n / d) )

for ac_file, output_mag_file, output_slope_file, output_phase_file in \
    zip(ac_files, output_mag_files, output_slope_files, output_phase_files):

    freq = []
    vo = []

    with open(ac_file, 'r') as f:
        for line in f:
            freq.append(float(line.split()[0]))
            vo_real = float(line.split()[1])
            vo_imag = float(line.split()[2])

            vo.append(vo_real + (vo_imag*1j) )
        
    vo_mag = np.abs(vo)
    vo_phase = np.angle(vo, deg = True)    
        
    labels = ['$f_{p1}$ = ', '$f_{p2}$ = ', '$f_z$ = ']
    angles = [135, 45, -45]
    guess = [1e2, 1e2, 1e6, 1e9]
    freq_rad = [2 * math.pi * f for f in freq]
    
    popt, pcov = curve_fit(fmag_2p1z, freq_rad, \
                           20*np.log10( vo_mag ), \
                           p0=guess)

    Ao_dB_calc = 20 * np.log10( popt[0] )
    
    index_vo0dB, vo0dB = eee51.find_in_data( 20*np.log10( vo_mag ), 0 )
    fu = freq[index_vo0dB]

    dAdf = np.diff(20*np.log10( vo_mag ))/np.diff(np.log10(freq_rad))

    # define the plot parameters
    plt_cfg = {
        'grid_linestyle' : 'dotted',
        'title' : r'Common-Emitter Amplifier Frequency Response',
        'xlabel' : r'Frequency [Hz]',
        'ylabel' : r'Magnitude [dB]',
        'legend_loc' : 'lower left',
        'add_legend' : False,
        'legend_title' : None
        }

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.set_ylim(-275, 75)

    ax.semilogx(freq, 20*np.log10(vo_mag), '-')

    eee51.add_hline_text(ax, Ao_dB_calc, 1e2, \
        r'$A_0$ = {:.1f}dB'.format(Ao_dB_calc))

    for w, label in zip(popt[1:], labels):
        eee51.add_vline_text(ax, w / (2 * math.pi ), -250, label + \
            si_format(w / (2 * math.pi ), precision=2) + 'Hz')

    eee51.add_vline_text(ax, fu, -250, r'$f_u=$' + \
            si_format(fu, precision=2) + 'Hz')

    eee51.label_plot(plt_cfg, fig, ax)
    plt.savefig(output_mag_file)

    # define the plot parameters
    plt_cfg = {
        'grid_linestyle' : 'dotted',
        'title' : r'Common-Emitter Amplifier Frequency Response',
        'xlabel' : r'Frequency [Hz]',
        'ylabel' : r'Magnitude Response Slope [dB/decade]',
        'legend_loc' : 'lower left',
        'add_legend' : False,
        'legend_title' : None
        }

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.set_ylim(-75, 10)

    ax.semilogx(freq[1:], dAdf, '-')

    for w, label in zip(popt[1:], labels):
        eee51.add_vline_text(ax, w / (2 * math.pi ), -70, label + \
            si_format(w / (2 * math.pi ), precision=2) + 'Hz')

    eee51.label_plot(plt_cfg, fig, ax)
    plt.savefig(output_slope_file)

    # define the plot parameters
    plt_cfg = {
        'grid_linestyle' : 'dotted',
        'title' : r'Common-Emitter Amplifier Frequency Response',
        'xlabel' : r'Frequency [Hz]',
        'ylabel' : r'Phase [degrees]',
        'legend_loc' : 'lower left',
        'add_legend' : False,
        'legend_title' : None
        }

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)

    ax.semilogx(freq, vo_phase, '-')

    for angle in angles:
        eee51.add_hline_text(ax, angle, 1e2, \
            r'{:.1f} deg'.format(angle))

    for w, label in zip(popt[1:], labels):
        eee51.add_vline_text(ax, w / (2 * math.pi ), -80, label + \
            si_format(w / (2 * math.pi ), precision=2) + 'Hz')

    eee51.label_plot(plt_cfg, fig, ax)
    plt.savefig(output_phase_file)
    
# transient results
    
tran_files = [cfg['tran_sim_1'], cfg['tran_sim_2'], cfg['tran_sim_3']]
output_tran_files = ['amp_ce_cm_tran_1_mag.png', 'amp_ce_cm_tran_2_mag.png', \
                    'amp_ce_cm_tran_3_mag.png']

fins = [1, 1e3, 5.13e3]

for tran_file, output_tran_file, fin in \
    zip(tran_files, output_tran_files, fins):
    
    flabel = r'($f_{in}=$' + si_format(fin, precision=2) + 'Hz)'
    
    t = []
    vi = []
    vo = []
    
    with open(tran_file, 'r') as f:
        for line in f:
            t.append(float(line.split()[0]))
            vi.append(float(line.split()[3]))
            vo.append(float(line.split()[1]))

    # define the plot parameters
    plt_cfg = {
        'grid_linestyle' : 'dotted',
        'title' : r'CE Amplifier Transient Response ' + flabel,
        'xlabel' : r'Time [s]',
        'ylabel' : r'Output Voltage [v]',
        'legend_loc' : 'upper left',
        'add_legend' : True,
        'legend_title' : None
        }

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax2 = ax.twinx()
    ax2.set_ylim(-15, 75)
    ax2.set_ylabel('Input Voltage [V]')

    ax.set_ylim( np.mean(vo) - ( 2.25 * ( np.mean(vo) - min(vo) )), \
                np.mean(vo) + ( 1.5 * ( max(vo) - np.mean(vo) )))

    vpp = si_format(max(vo) - min(vo), precision=2) + 'V'
    
    ax.plot(t, vo, '-', color='red', \
        label = r'$v_{out}, V_{p-p}=$' + vpp)
    
    ax2.plot(t, eee51.scale_vec(vi, g51.milli), '-', \
        label = r'$v_{in}$')

    ax2.legend(loc='upper right')
    
    eee51.label_plot(plt_cfg, fig, ax)
    plt.savefig(output_tran_file)
