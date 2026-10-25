# compare model.step (with y=1 transfer done) to literal simulation for many (P, c)
from dfam import nextD
from model import step
import itertools,sys
bad=0;n=0
def expand(runs):
    out=[]
    for d,k in runs: out+= [d]*k
    return tuple(out)
for P in [()]+[(e,) for e in range(1,13)]+[(a,e) for a in (1,2,5) for e in (3,6,9,4,8)]+[(2,1,3),(1,1,1,5)]:
    for c in range(1,31):
        ds=P+(c,)
        r=nextD(ds,1,5000000)
        runs=[]
        for d in ds:
            if runs and runs[-1][0]==d: runs[-1][1]+=1
            else: runs.append([d,1])
        m=step(runs,1)
        n+=1
        if isinstance(m[2],tuple):
            ok = r is not None and r[1]=="HALT"
        else:
            ok = r is not None and r[1]!="HALT" and expand(m[0])==r[1] and m[1]==r[2]
        if not ok:
            bad+=1; print("MISMATCH",ds,r,m)
print(n,"cases",bad,"mismatches")
