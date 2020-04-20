#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 20 10:36:48 2020

@author: louis
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 16 18:29:11 2020

@author: louis
"""

import matplotlib.pyplot as plt
import eee51, g51 

# load constants and global variables, referenced by g51.*
g51.init_global_constants()

specs = {
        'ic' : 1e-3,
        'vce' : 2.5
        }
    
# run ngspice
cfg = {
        'spice' : '/Applications/ngspice/bin/ngspice', 
        'cir_dir' : '/Users/louis/Documents/UPEEEI/Classes/EEE 51/Mini Projects/',
        'cir_file' : 'circuit3.sp',
        'transfer_data' : 'bjt_transfer_sim.dat',
        'output_data' : 'bjt_output_sim.dat'
        }

# note: you can do this from the command line and just process the data files
# this was done here for convenience
eee51.run_spice(cfg)

# to get the rest of the BJT parameters, let's use the transfer characteristics
# open the transfer characteristics data file and get the data
vbe = []    # declare list for vbe
ic2 = []    # declare a list for ic with vce = 2.5V
            # we'll use this to check our model
ib2 = []    # declare a list for the base currents at vce = 2.5V
            
with open(cfg['transfer_data'], 'r') as f:
    for line in f:
        vbe.append(float(line.split()[0]))
        ic2.append(float(line.split()[3]))
        ib2.append(float(line.split()[5]))

# convert to mV
vbe_mV = eee51.scale_vec(vbe, g51.milli)

# plot the transistor dc beta
g51.update_bjt_VA(-15.550605626760145) 
bjt_n = 1.2610858394025979
bjt_Is = 6.924988420125876e-13

# calculate the vbe needed for vce = 2.5V
reqd_vbe = eee51.bjt_find_vbe(specs['ic'], specs['vce'], \
    bjt_Is, bjt_n, g51.bjt_VA)

bjt_beta = [a/b for a, b in zip(ic2, ib2)]

index, vbe_sim = eee51.find_in_data(vbe, reqd_vbe)

plt_cfg = {
        'grid_linestyle' : 'dotted',
        'title' : r'BJT 2N2222A DC $\beta_{DC}$',
        'xlabel' : r'$V_{BE}$ [mV]',
        'ylabel' : r'$\beta$',
        'legend_loc' : 'upper left',
        'add_legend' : False,
        'legend_title' : None
        }

fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
ax.plot(vbe_mV, bjt_beta, \
    label = 'simulation ($V_{CE}$=2.5V)')

eee51.add_vline_text(ax, reqd_vbe/g51.milli, 10, '$V_{BE}$ = ' + \
    '{:.1f}mV'.format(reqd_vbe/g51.milli))

eee51.add_hline_text(ax, bjt_beta[index], 550, \
    r'$\beta_{DC}=$' + '{:.2f}'.format(bjt_beta[index]))

eee51.label_plot(plt_cfg, fig, ax)
plt.savefig('2N2222A_beta_dc.png')

