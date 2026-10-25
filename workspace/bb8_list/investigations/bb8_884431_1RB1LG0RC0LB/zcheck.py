import sys
from fam import *
bad=0;tot=0
for n in range(1,15):
    for b in range(0,5):
        r=run_next([0]*n,0,b,N=3000000)
        if n==1: p=((b+4,0,0),0,0)
        elif n%2==1: p=((((n+1)//2),)+(0,)*(2*b+4),0,0)
        else: p=((),(2*n+8)*2**b-3,1)
        tot+=1
        if not(r[0]=='K' and r[2]==p):
            bad+=1; print('MISMATCH',n,b,r[:3] if r[0]!='HALT' else 'HALT',p if len(str(p))<100 else '..',flush=True)
print(tot,bad)
