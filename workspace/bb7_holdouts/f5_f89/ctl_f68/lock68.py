import sys
from f68eng import parse,step,show,margin
from collections import Counter
mins={};mj={}
prev=None; miss=0; n=0; rc=Counter(); bad=0
for line in open(sys.argv[1]):
    p=line.split(None,1)
    if len(p)<2 or not p[0].isdigit(): continue
    st=parse(p[1])
    if st is None: bad+=1; continue
    if prev is not None:
        nx,r=step(prev); rc[r if r in ("D","T0") else r[0]+"j"]+=1; n+=1; mg=margin(prev)
        if mg: mins[mg[0]]=min(mins.get(mg[0],10**18),mg[2]); mj[mg[0]]=max(mj.get(mg[0],0),mg[1])
        if nx!=st:
            miss+=1
            if miss<5: print('MISS',show(prev),r,'->',show(nx) if nx else None,'lit',show(st))
    prev=st
print('pairs',n,'miss',miss,'nontemplate lines',bad); print(dict(rc))
print('last',show(prev))
print("min margin by rule",mins,"max depth",mj)
