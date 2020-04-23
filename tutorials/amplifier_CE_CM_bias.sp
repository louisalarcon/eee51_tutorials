* Common Emitter Amplifier with Current Mirror Bias
* LPA 2020-04-16

.include 2N390X.lib
.options savecurrents

Vcc		v1	0		dc 5.0

* the pnp current mirror
Q2		vout b2 v1	2N3906
Q3		b2 b2 v1	2N3906

* the bias resistor
Rm		b2 0		5.277k

* the npn gain transistor
Q1		vout b1 0	2N3904

Vin 	b1 b1a		dc 0 sin(0 10m 1k)
Vbe1	b1a 0		dc 662.22m

.control

dc Vin -100m 100m 1m
wrdata amp_ce_cm_transfer_sim.dat v(vout) @Q1[ic]

alter Vbe1 dc = 666m
dc Vin -100m 100m 1m
wrdata amp_ce_cm_transfer_sim2.dat v(vout) @Q1[ic]
 
.endc

.end
