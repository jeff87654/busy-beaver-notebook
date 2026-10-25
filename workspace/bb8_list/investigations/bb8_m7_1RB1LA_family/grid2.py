import sys,itertools,random
import kd
from kd import *
import kfam
from kfam import strip, trailing_zeros, run_next
def predict(ds,a,b):
    ds=list(ds)
    if a>=1: return (tuple(ds),a-1,b+1)
    k=trailing_zeros(ds)
    if k==len(ds): return ((2,)*b,2,0)
    i=len(ds)-1-k
    if k==0:
        ds[-1]-=1; return (strip(ds),2*b+2,0)
    pre=ds[:i]; y1=ds[i]
    if b>=k+1: new=pre+[y1-1,2*(b-k+1)]+[2]*(k-1)
    elif b==k: new=pre+[y1+2]+[2]*(k-1)
    else: new=pre+[y1]+[0]*(k-b-1)+[2]*b
    return (strip(new),2,0)
def literal(tm,ds,a,b,N=3*10**6):
    r=run_next(tm,ds,a,2*b+1,N=N)
    if r[0]=='K':
        d,aa,bu=r[2]
        if bu%2!=1: return ('BADBU',r)
        return ('K',(d,aa,(bu-1)//2),r[1])
    return r
def cases(maxdig=3,maxval=3):
    cs=[]
    for n in range(0,maxdig+1):
        for ds in itertools.product(range(0,maxval+1),repeat=n):
            if ds and ds[0]==0: continue
            for a in range(0,3):
                for b in range(0,6):
                    cs.append((ds,a,b))
    for b in range(1,8):
        for k in range(1,10):
            for y in (1,2,3):
                for pre in ((),(2,),(1,3)):
                    cs.append((pre+(y,)+(0,)*k,0,b))
    return cs
def check(tm,verbose=40):
    bad=0;tot=0
    for ds,a,b in cases():
        if a==0 and b==0: continue
        if a==0 and not ds: continue
        if a==0 and ds and trailing_zeros(ds)==len(ds) and False: continue
        # all-zero list with leading zeros: tape-equivalent to empty; skip non-normalized
        if ds and ds[0]==0: continue
        p=predict(ds,a,b); l=literal(tm,ds,a,b)
        tot+=1
        if l[0]!='K' or l[1]!=p:
            bad+=1
            if bad<=verbose: print('MISMATCH',ds,a,b,'pred',p,'lit',l[:3] if l[0]=='K' else l[:3])
    return tot,bad
if __name__=='__main__':
    tm=sys.argv[1] if len(sys.argv)>1 else TM
    print(tm,check(tm))
