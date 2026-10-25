"""Literal check of the rule-level family rules (rules.py) on the mirror machine, incl. b=0 and zero digits."""
import os, itertools
os.environ['BB_KENC'] = '10,0'
from kfam import run_next, set_shape, show
import rules
set_shape('A', '111')
TM = '1LB0LG_1RC1LE_1RD0RD_0LA1RC_0LF0RC_1RG1LH_1LB1LG_1LF---'.replace('1LB1LG_1LF','1RB1LG_1LF')
TM = '1LB0LG_1RC1LE_1RD0RD_0LA1RC_0LF0RC_1RG1LH_1RB1LG_1LF---'
st={}; bad=[]
def grid():
    for n in range(0,4):
        for ds in itertools.product(range(0,4),repeat=n):
            if ds and ds[0]==0: continue
            for a in range(0,4):
                for b in range(0,6): yield ds,a,b
    for b in range(0,9):
        for k in range(1,b+6):
            for y in (1,2):
                yield (1,y)+(0,)*k,0,b
for ds,a,b in grid():
    kd,p=rules.step(ds,a,b)
    if p is None: st.setdefault(kd,[0,0]); st[kd][0]+=1; continue
    r=run_next(TM,ds,a,b,N=10**6)
    got=r[2] if r[0]=='K' else None
    if a==1 and not ds:   # K(;1;b) -> R1 then R4 in one literal run
        kd2,p2=rules.step(*p); 
        if kd2=='R4': p=p2[0:3]
    ok = got==p
    st.setdefault(kd,[0,0]); st[kd][0]+=1; st[kd][1]+=ok
    if not ok: bad.append((kd,ds,a,b,got,p))
print({k:tuple(v) for k,v in st.items()})
for x in bad[:20]: print('BAD',x)
