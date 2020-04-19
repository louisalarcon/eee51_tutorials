#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 15:36:28 2020

@author: louis
"""
import subprocess
# import matplotlib.pyplot as plt
# from scipy.optimize import curve_fit
import numpy as np
# from si_prefix import si_format
# import math
# from statistics import mean
import g51


def celsius_to_kelvin(temp):
    return temp + 273.15

def run_spice(cfg):
    # run ngspice from the command line
    cli_cmd = [cfg['spice'], cfg['cir_dir'] + cfg['cir_file']]
    process = subprocess.Popen(cli_cmd, \
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    stdout, stderr = process.communicate()
    print(stdout.decode('utf-8'))
    # uncomment the line below to see error messages
    # print(stderr.decode('utf-8'))

def scale_vec(value, f):       
    return [v/f for v in value]

def ideal_bjt_transfer(vbe, Is, n):
    # VT = g51.constants['k'] * g51.constants['T'] / g51.constants['q']
    # n = 1.00 (ideal) n ~ 1.25 to account for low field currents
    return Is * np.exp( vbe / (n * g51.VT) ) * ( 1 + (g51.bjt_vce/abs(g51.bjt_VA)) )

def bjt_find_vbe(ic, vce, Is, n, VA):
    # VT = g51.constants['k'] * g51.constants['T'] / g51.constants['q']
    return np.log( ic / (Is * ( 1 + (vce/abs(VA)) ))) * (n * g51.VT)

def line_eq(x, m, b):
    return (m * x) + b

# calculate the index and closest value (in a list) to a given number
def find_in_data(data, value):
    index, closest = min(enumerate(data), key=lambda x: abs(x[1] - value))
    return index, closest

# i don't want to type this everytime i plot a graph
def label_plot(plt_cfg, fig, ax):
    ax.grid(True)
    ax.grid(linestyle=plt_cfg['grid_linestyle'])
    ax.set_title(plt_cfg['title'])
    ax.set_xlabel(plt_cfg['xlabel'])
    ax.set_ylabel(plt_cfg['ylabel'])
    if plt_cfg['add_legend']:
        ax.legend(loc=plt_cfg['legend_loc'], title=plt_cfg['legend_title'])
    fig.set_tight_layout('True')
    
# i don't want to type this everytime i plot a graph
def add_vline_text(ax, xd, ypos, txt_label):
    ax.axvline(x=xd, color='black', linestyle='-.', linewidth=1)
    ax.text(xd, ypos, txt_label, \
        rotation=90, color='black', \
        horizontalalignment='right', verticalalignment='bottom')
    
# i don't want to type this everytime i plot a graph
def add_hline_text(ax, yd, xpos, txt_label):
    ax.axhline(y=yd, color='black', linestyle='-.', linewidth=1)
    ax.text(xpos, yd, txt_label,\
        rotation=0, color='black', \
        horizontalalignment='left', verticalalignment='bottom')
    
# parallel resistors
def r_parallel(r_array):
    gt = 0
    for r in r_array:
        gt += 1/r
        
    return 1/gt


