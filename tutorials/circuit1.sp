* Transistor Characteristic Curves
* LPA 2020-04-16

.include 2N2222A.lib
.options savecurrents

Q1		c1 b1 0		Q2n2222a
Vbe		b1 0		dc 0
Vce		c1 0 		dc 0.2

.control

dc Vbe 500m 750m 1m
plot @Q1[ic]
wrdata circuit1.dat @Q1[ic]

.endc

.end
