* Common Emitter Amplifier with Current Mirror Bias
* LPA 2020-04-16

.include 2N390X.lib
.options savecurrents

.param freqin = 1

Vcc		v1	0		dc 5.0

* the pnp current mirror
Q2		vout b2 v1	2N3906
Q3		b2 b2 v1	2N3906
C2		b2 v1		10u

* the bias resistor
Rm		b2 0		5.277k
* Rm		b2 0		5.1k

* the npn gain transistor
Q1		vout b1 0	2N3904
Cu		b1 vout 	10p

Vin 	b1b b1a		dc 0 ac 1 sin(0 10m {freqin})
Rs		b1b b1		50
Cin		b1 0		10n

Cload	vout 0		1u

* the npn current mirror
Q4		b1a b1a 0	2N3904
Rm2		v1 b1a		5.352k
C1		b1a 0 		10u

.control

ac dec 100 1 100G
wrdata amp_ce_cm_ac_1_sim.dat v(vout)

alter Cload = 5u
ac dec 100 1 100G
wrdata amp_ce_cm_ac_2_sim.dat v(vout)

alter Cload = 1u 
alter Cu = 50p
ac dec 100 1 100G
wrdata amp_ce_cm_ac_3_sim.dat v(vout)

alter Cu = 10p
alter Cin = 50n 
ac dec 100 1 100G
wrdata amp_ce_cm_ac_4_sim.dat v(vout)

alter Cload = 1u 
alter Cu = 10p
alter Cin = 10n 

op
tran 1m 10 5 
wrdata amp_ce_cm_transient_1_sim.dat v(vout) v(b1b)-v(b1a)

alterparam freqin = 1k
reset
tran 1u 105m 100m 
wrdata amp_ce_cm_transient_2_sim.dat v(vout) v(b1b)-v(b1a)

alterparam freqin = 5.13k
reset
tran 200n 23.22m 22.22m
wrdata amp_ce_cm_transient_3_sim.dat v(vout) v(b1b)-v(b1a)

.endc

.end
