* Transistor Characteristic Curves
* LPA 2020-04-16

.include 2N2222A.lib
.options savecurrents

Q1		c1 b1 0		Q2n2222a
Vbe		b1 0		dc 0
Vce		c1 0 		dc 0.2

Q2		c2 b1 0		Q2n2222a
Vce2	c2 0 		dc 2.5

.control

dc Vbe 500m 750m 1m
wrdata bjt_transfer_sim.dat @Q1[ic] @Q2[ic] @Q2[ib]

dc Vce 30m 5 10m Vbe 0.65 0.7 0.01
wrdata bjt_output_sim.dat @Q1[ic]
 
.endc

.end
