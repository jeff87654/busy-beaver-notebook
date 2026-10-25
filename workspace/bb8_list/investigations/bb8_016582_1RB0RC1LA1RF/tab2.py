from fam import *
import sys
print("j=5 (2 mod 3), a=1, ds=(d,) and (d,20)")
for d in range(0,13):
    print(d, step_R(5,1,(d,)), step_R(5,1,(d,20)))
print("j=7 (1 mod 3), a=1..8, ds=(),(9,)")
for a in range(1,9):
    print(a, step_R(7,a,()), step_R(7,a,(9,)))
