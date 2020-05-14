**************************************************
* differential input single-ended output amplifier
.subckt diffamp_n vip vin vo vcc

* input pair
Q1		c3 vip vx		2N3904
Q2		vo vin vx		2N3904

* current mirror load
Q3		c3 b34 vcc		2N3906
Q4		vo b34 vcc		2N3906
Q5		0 c3 b34		2N3906

* tail current source
Q6		vx b67 e6		2N3904
Q7		c7 b67 e7		2N3904
Q8		vcc c7 b67		2N3904

* tail current degeneration
Re6		e6 0 			100
Re7		e7 0 			100

* bias resistor
Rm		vcc c7			{Rmdiff}

.ends diffamp_n
