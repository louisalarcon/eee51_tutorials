#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 17:07:49 2020

@author: louis
"""

def init_global_constants():
    global constants, milli, VT
    
    constants = {
        'k' : 1.38064852e-23,   # J/K
        'q' : 1.60217662e-19,   # C
        'T' : 300               # K
        }
    
    milli = 1e-3
    VT = constants['k'] * constants['T'] / constants['q']

    
def update_bjt_vce(a):
    global bjt_vce
    bjt_vce = a
    
def update_bjt_VA(a):
    global bjt_VA
    bjt_VA = a

