* Common Emitter Amplifiers
* LPA 2020-04-18

.include 2N2222A.lib
.options savecurrents

Q1		c1 b1 0	Q2n2222a
Rc	 	v1 c1	2.5k
Vcc		v1 0	dc 5
Vin		b1 b1a	dc 0 sin(0 10m 1k)
Vbe		b1a 0	dc 682.73m

.control

dc Vin -100m 100m 1m
wrdata ce_amp_transfer_sim.dat v(c1) @Q1[ic]

tran 1u 5m
wrdata ce_amp_transient_sim.dat v(b1) v(c1) 

.endc

.end
