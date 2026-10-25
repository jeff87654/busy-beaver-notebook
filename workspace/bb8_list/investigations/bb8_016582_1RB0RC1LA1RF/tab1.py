from fam import *
import sys
for j in range(1,14):
    for a in (1,2,5):
        for ds in ((),(12,),(12,20)):
            r=step_R(j,a,ds)
            print(j,a,ds,r)
