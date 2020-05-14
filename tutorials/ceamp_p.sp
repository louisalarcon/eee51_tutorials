******************************
* pnp common emitter amplifier
.subckt ceamp_p vi vo vcc

* gm (gain) transistor
Q1		vo vi e1		2N3906
Re1		e1 vcc			{Repce}

* current mirror load
Q2		vo b23 e2		2N3904
Q3		c3 b23 e3		2N3904
Q4		vcc c3 b23		2N3904

Re2		e2 0 			{Rence}
Re3		e3 0 			{Rence}

Rm		vcc c3			{Rmce}

.ends ceamp_p
