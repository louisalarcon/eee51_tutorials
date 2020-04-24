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
* Rm		b2 0		5.1k

* the npn gain transistor
Q1		vout b1 0	2N3904

Vin 	b1 b1a		dc 0 sin(0 10m 1k)

* the npn current mirror
Q4		b1a b1a 0	2N3904
Rm2		v1 b1a		5.352k
* Rm2		v1 b1a		5.1k

.control

dc Vin -100m 100m 1m
wrdata amp_ce_cm2_transfer_sim.dat v(vout) @Q1[ic]

tran 1u 5m 
wrdata amp_ce_cm2_transient_sim.dat v(vout) v(b1)

.endc

.end
