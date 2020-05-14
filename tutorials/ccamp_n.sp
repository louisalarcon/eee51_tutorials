*************************************
* npn output stage (common collector)
.subckt ccamp_n vi vo vcc

Q1		vcc vi vo		2N3904

* current mirror bias
Q2		vo b23 0		2N3904
Q3		c3 b23 0		2N3904
Q4		vcc c3 b23		2N3904

Rm		vcc c3			{Rmcc}

.ends ccamp_n
