* A simple 3-stage opamp
* LPA 2020-04-16

.include 2N390X.lib
.options savecurrents

.include diffamp_n.sp
.include ceamp_p.sp
.include ccamp_n.sp

* calculated values
* .param Rmdiff = 1.788k Rmce = 3.161k Rmcc = 3.823k Repce = 545 Rence = 672

* tweaked values 
.param Rmdiff = 1.722k Rmce = 3.161k Rmcc = 3.823k Repce = 545 Rence = 672

* instantiate the 3 amplifiers
X1		vip vin vo1 vcc		diffamp_n
X2		vo1 vo2 vcc			ceamp_p
X3		vo2 vo3 vcc			ccamp_n

* supply voltage
V1		vcc 0 			5.0

* voltage controlled voltage sources to generate vip and vin from vid
E1		vip vic vid 0	0.5
E2		vic vin vid 0	0.5

* differential input
Vdm 	vid 0		dc 0 sin(0 100u 1k)

* common mode input
Vcm		vic 0		dc 1.8


.control

* let's check the DC voltages and currents using the DC operating point (op) analysis
op
print @Q.X1.Q1[ic] @Q.X1.Q2[ic] @Q.X1.Q6[ic] 
print @Q.X2.Q1[ic] @Q.X2.Q2[ic]
print @Q.X3.Q1[ic] @Q.X3.Q2[ic]
print v(vo1) v(vo2) v(vo3)

dc Vdm -1m 1m 25u
wrdata opamp1_vic=1.8_sim.dat v(vo1) v(vo2) v(vo3) v(X1.vx)
+ @Q.X1.Q1[ic] @Q.X1.Q2[ic] @Q.X1.Q6[ic]
+ @Q.X2.Q1[ic] @Q.X2.Q2[ic] 
+ @Q.X3.Q1[ic] @Q.X3.Q2[ic] 

* plot v(vo1) v(vo2) v(vo3) v(X1.vx)
* plot @Q.X1.Q1[ic] @Q.X1.Q2[ic] @Q.X1.Q6[ic]
* plot @Q.X2.Q1[ic] @Q.X2.Q2[ic] 
* plot @Q.X3.Q1[ic] @Q.X3.Q2[ic] 

tran 1u 5m
wrdata opamp1_tran_vic=1.8_sim.dat v(vid) v(vo1) v(vo2) v(vo3)
+ @Q.X1.Q1[ic] @Q.X1.Q2[ic] @Q.X1.Q6[ic]
+ @Q.X2.Q1[ic] @Q.X2.Q2[ic] 
+ @Q.X3.Q1[ic] @Q.X3.Q2[ic] 
* plot v(vo3) v(vip)

.endc

.end

