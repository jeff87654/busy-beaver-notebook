import sys,itertools
from kd import *
from kfam import strip, trailing_zeros
def predict(ds,a,b):
    # b = number of "b" in bu=2b+1
    ds=list(ds)
    if a>=1: return ('K',(tuple(ds),a-1,b+1))
    k=trailing_zeros(ds)
    if k==len(ds): return ('K',((2,)*b,2,0))
    i=len(ds)-1-k
    if k==0:
        ds[-1]-=1; return ('K',(strip(ds),2*b+2,0))
    ds=ds[:i+1]; ds[i]-=1
    ds=ds+[2*b]+[1]*(k-1)
    return ('K',(strip(ds),2,0))
def literal(ds,a,b,N=3*10**6):
    r=run_next(TM,ds,a,2*b+1,N=N)
    if r[0]=='K':
        d,aa,bu=r[2]
        assert bu%2==1
        return ('K',(d,aa,(bu-1)//2),r[1])
    return r
bad=0;tot=0
cases=[]
for n in range(0,4):
    for ds in itertools.product(range(0,4),repeat=n):
        if ds and ds[0]==0: continue
        for a in range(0,3):
            for b in range(0,6):
                cases.append((ds,a,b))
for b in range(0,4):
    for k in range(1,2*b+8):
        for y in (1,2):
            cases.append(((1,y)+(0,)*k,0,b))
for ds,a,b in cases:
    if b==0 and a==0: continue
    if not ds and a==0: continue
    if not ds and a==1 and False: continue
    p=predict(ds,a,b); l=literal(ds,a,b)
    tot+=1
    if l[0]!='K' or l[1]!=p[1]:
        bad+=1
        if bad<=40: print('MISMATCH',ds,a,b,'pred',p,'lit',l[:3] if l[0]=='K' else l)
print(tot,'cases',bad,'mismatches')
