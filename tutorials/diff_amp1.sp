* A BJT Differential Amplifier
* LPA 2020-04-16

.include 2N390X.lib
.options savecurrents

Vcc		v1	0		dc 5.0

* diff pair
Q1		vop vip vx		2N3904
Q2		von	vin	vx		2N3904

* tail current source
* Re3 is a placeholder for the degeneration resistor
Q3		vx bm e3		2N3904
Re3		e3 0			0

* Re4 is a placeholder for the degeneration resistor
Q4		bm bm e4		2N3904
Re4		e4 0 			0

* load resistors
RLp		v1 vop			1.5k
RLn		v1 von			1.5k

* tail current bias resistor
Rm 		v1 bm			2.122k

* voltage controlled voltage sources to generate vip and vin from vid
E1		vip vic vid 0	0.5
E2		vic vin	vid 0	0.5

* differential input
Vdm 	vid 0		dc 0 sin(0 30m 1k)

* common mode input
Vcm		vic 0		dc 1.2


.control

dc Vcm 0.5 3.5 0.01
wrdata diff_amp1_vcm_Re=0_sim.dat @Q3[ic] v(vop)

alter Re3 = 50 
alter Re4 = 50
alter Rm = 2.073k

dc Vcm 0.5 3.5 0.01
wrdata diff_amp1_vcm_Re=50_sim.dat @Q3[ic] v(vop)

dc Vdm -0.2 0.2 0.25m
wrdata diff_amp1_vic=1.2_Re=50_sim.dat v(vop) v(von) v(vx) @Q1[ic] @Q2[ic] @Q3[ic]

alter Vcm dc = 1.8
dc Vdm -0.2 0.2 0.25m
wrdata diff_amp1_vic=1.8_Re=50_sim.dat v(vop) v(von) v(vx) @Q1[ic] @Q2[ic] @Q3[ic]

tran 1u 5m 
wrdata diff_amp1_transient_sim.dat v(vop) v(von) v(vip) v(vin) v(vx) 
+ @Q1[ic] @Q2[ic] @Q3[ic]

alter Vcm dc = 2.4
dc Vdm -0.2 0.2 0.25m
wrdata diff_amp1_vic=2.4_Re=50_sim.dat v(vop) v(von) v(vx) @Q1[ic] @Q2[ic] @Q3[ic]

alter Re3 = 100 
alter Re4 = 100
alter Rm = 2.024k

dc Vcm 0.5 3.5 0.01
wrdata diff_amp1_vcm_Re=100_sim.dat @Q3[ic] v(vop)

alter Vcm dc = 1.2
dc Vdm -0.2 0.2 0.25m
wrdata diff_amp1_vic=1.2_Re=100_sim.dat v(vop) v(von) v(vx) @Q1[ic] @Q2[ic] @Q3[ic]

alter Vcm dc = 1.8
dc Vdm -0.2 0.2 0.25m
wrdata diff_amp1_vic=1.8_Re=100_sim.dat v(vop) v(von) v(vx) @Q1[ic] @Q2[ic] @Q3[ic]

tran 1u 5m 
wrdata diff_amp1_transient_Re=100_sim.dat v(vop) v(von) v(vip) v(vin) v(vx) 
+ @Q1[ic] @Q2[ic] @Q3[ic]

alter Vcm dc = 2.4
dc Vdm -0.2 0.2 0.25m
wrdata diff_amp1_vic=2.4_Re=100_sim.dat v(vop) v(von) v(vx) @Q1[ic] @Q2[ic] @Q3[ic]

.endc

.end
