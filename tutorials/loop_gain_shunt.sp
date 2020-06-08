* Shunt-Feedback Amplifier with Current Mirror Bias
* LPA 2020-04-16

.include 2N390X.lib
.options savecurrents

.param freqin = 1 Rs = 125k Rf = 250k

Vsup	vcc	0		dc 5.0

.subckt ce_amp vip vin vout vcc
* the pnp current mirror
Q2		vout b2 vcc	2N3906
Q3		b2 b2 vcc	2N3906
C2		b2 vcc		10u

* the bias resistor
Rm		b2 0		5.277k

* the npn gain transistor
Q1		vout vip 0	2N3904
Cu		vip vout 	10p
Cin		vip 0		10n
Cload	vout 0		1u

* the npn current mirror
Q4		vin vin 0	2N3904
Rm2		vcc vin		5.352k
C1		vin 0 		10u
.ends ce_amp

* loop gain measurement DUT
X1			vip1 vin1 vout1 vcc 	ce_amp

Vin1 		vx1 vin1		dc 0 ac 1 sin(0 200m {freqin})
Rs1			vx1 vya			{Rs}
Rf1			vout1 vy1		{Rf}
Linf1		vy1a vya		1k

* dummy voltage sources to measure current 
Verr1		vya	vip1		dc 0
Vfb1		vy1a vy1		dc 0

* using current-controlled voltage sources
* convert current to voltage to be able to plot in dB
H1			viin 0 			Verr1 1.0
H2			vifb 0 			Vfb1 1.0

* replica load amp
X2			vy2 vin2 vout2 vcc		ce_amp

Cinf		vy1a vy2		1k
Rs2			vip2 vin2		{Rs}
Rf2			vout2 vy2		{Rf}
Linf2		vy2 vip2		1k

* closed loop amp to get the closed-loop response
X3 			vip3 vin3 vout3 vcc		ce_amp

Vin3 		vx3 vin3		dc 0 ac 1 sin(0 200m {freqin})
Rs3			vx3 vx3a		{Rs}
Rf3			vout3 vip3		{Rf}
Viin3		vx3a vip3 		dc 0

* using current-controlled voltage sources
* convert current to voltage to be able to plot in dB
H3			viincl 0			Viin3 1.0

.control

op
print @Q.X1.Q1[ic] @Q.X1.Q2[ic] v(vout1) 
print @Q.X2.Q1[ic] @Q.X2.Q2[ic] v(vout2) 
print @Q.X3.Q1[ic] @Q.X3.Q2[ic] v(vout3) 
print v(viin) v(vifb)
print @Rf1[i] @Rs1[i]

ac dec 100 1 100G
wrdata loop_gain_shunt_ac.dat v(vout3) v(vifb) v(viin) v(vout1) v(viincl)

tran 1m 10 5 
wrdata loop_gain_shunt_transient_1.dat v(vout3) v(vx3)-v(vin3)

.endc

.end
