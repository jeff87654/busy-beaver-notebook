import sys
sys.path.insert(0,'.')
import tr
from fam import run_next
import itertools
P0=tr.TM
P1=P0[:-3]+'1RH'
bad=0; steps={}
for tm in (P0,P1):
    for n in range(0,7):
        for b in range(0,7):
            r=run_next([0]*n,0,b,N=10**7,tm=tm)
            ok = r[0]=='K' and r[2]==([2]+[0]*(12*b+n+6),0,0)
            if not ok: bad+=1; print('BAD',tm[-3:],n,b,r[:2])
            steps[(tm[-3:],n,b)]=r[1]
print('bad',bad)
# fit steps(n,b) = alpha b^2 + beta b + gamma + n*(delta + eps b)
import numpy as np
rows=[];ys=[]
for (t,n,b),s in steps.items():
    if t=='1RF': rows.append([b*b,b,1,n,n*b,n*n]); ys.append(s)
sol=np.linalg.lstsq(np.array(rows,float),np.array(ys,float),rcond=None)
print(sol[0].round(4), 'resid',sol[1])
print(all(steps[('1RF',n,b)]==steps[('1RH',n,b)] for n in range(7) for b in range(7)))
