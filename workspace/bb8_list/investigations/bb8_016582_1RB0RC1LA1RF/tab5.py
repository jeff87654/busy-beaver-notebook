from fam import *
print("R(j,1|1,S)")
for j in (2,5,8,11):
    print(j, step_R(j,1,(1,)), step_R(j,1,(1,30)), step_R(j,1,(1,3,30)),flush=True)
print("class 0")
for j in (3,6,9,12,15):
    for a in (1,2,3,4,5,6):
        print(j,a, step_R(j,a,()), step_R(j,a,(30,)),flush=True)
