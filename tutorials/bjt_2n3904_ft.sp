* Transistor transition frequency
* LPA 2020-04-16

.include 2N390X.lib

.options savecurrents

* the npn 2N3904 transistor
Q1		c1 b1 0		2N3904

Iin1 	b1 0		dc 0 ac 1
Lblk1	b1a b1		1k

* the npn current mirror
Q1a		c1x b1a 0		2N3904
Q1b		vcc c1x b1a		2N3904
Im1		vcc c1x		0.9m
V1		c1 0 		dc 2.5

Vsup	vcc 0 		dc 2.5

.control

op
let ft_2n3904_sim = '@Q1[gm]/(2*3.14*(@Q1[cpi]+@Q1[cmu]))'
print @Q1[ic] @Q1[gm] @Q1[cpi] @Q1[cmu] ft_2n3904_sim

ac dec 1000 100k 10G
wrdata bjt_2n3904_ft_1mA_sim.dat i(V1)

let mag_iV1 = abs(i(V1))
meas ac ft_2n3904 when mag_iV1=1

alter Im1 = 9m

op
let ft_2n3904_sim = '@Q1[gm]/(2*3.14*(@Q1[cpi]+@Q1[cmu]))'
print @Q1[ic] @Q1[gm] @Q1[cpi] @Q1[cmu] ft_2n3904_sim

ac dec 1000 100k 10G
wrdata bjt_2n3904_ft_10mA_sim.dat i(V1)

let mag_iV1 = abs(i(V1))
meas ac ft_2n3904 when mag_iV1=1

.endc

.end
