* Common Emitter Amplifier with Current Mirror Bias
* LPA 2020-04-16

.include 2N390X.lib
.options savecurrents

Vcc		v1	0		dc 5.0

* first stage
* the pnp current mirror
Q2		vout1 b2 v1	2N3906
Q3		b2 b2 v1	2N3906

* the bias resistor
Rm		b2 0		6.312k

* the npn gain transistor
Q1		vout1 b1 0	2N3904

Vin 	b1 b1a		dc 0 sin(0 125u 1k)

* the npn current mirror
Q4		b1a b1a 0	2N3904
Rm2		v1 b1a		4.267k

* second stage
* the pnp current mirror
Q6		vout b22 v1	2N3906
Q7		b22 b22 v1	2N3906

* the bias resistor
Rm3		b22 0		5.277k

* the npn gain transistor
Q5		vout vout1 0	2N3904


.control

dc Vin -0.5m 0.5m 5u
wrdata amp_2stage_transfer_sim.dat v(vout) @Q1[ic] @Q5[ic]

tran 1u 5m 
wrdata amp_2stage_transient_sim.dat v(vout) v(b1) v(vout1)

.endc

.end
