import sys,os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from w_fam import *
R = rules2()
import itertools
def grid(names):
    return {k:list(range(0,4)) for k in names}
tests={'R1m':['a','b'],'R3Am':['k','r','y'],'R3Bm':['c','y'],'R3Cm':['c','m','y'],'R4m':['c']}
for nm,vs in tests.items():
    s,t=R[nm]
    bad=0;tot=0
    for vals in itertools.product(range(0,4),repeat=len(vs)):
        v=dict(zip(vs,vals))
        for extra in ('a','b','c','k','r','y','m'):
            v.setdefault(extra,0)
        r=validate.reaches(s,t,v,max_steps=300000)
        tot+=1
        if r is None:
            bad+=1
            if bad<=3: print(nm,'FAIL',v)
    print(nm,tot,'cases',bad,'failures')
