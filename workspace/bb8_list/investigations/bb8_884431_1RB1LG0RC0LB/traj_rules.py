"""Literal run from the blank tape vs rule-level successor of every family configuration (ds farthest-first)."""
import sys
from fam import *
def succ(ds,a,b):
    ds=list(ds)
    if a>=1: return (tuple(ds),a-1,b+2)
    k=0
    while ds and ds[-1]==0: ds.pop(); k+=1
    if ds:
        y1=ds.pop()
        if k==0: return (tuple(ds+[y1-1]),b+2,0)
        return (tuple(ds+[y1-1,b+2]+[0]*(k-1)),0,0)
    n=k   # all zero list of length n
    assert n%2==1,('even',n)
    if n==1: return ((b+4,0,0),0,0)
    return (((n+1)//2,)+(0,)*(2*b+4),0,0)
N=int(sys.argv[1])
m=M(); prev=None; cnt=0; bad=0; maxb=0; kinds={}
while m.n<N:
    if not m.step(): print('HALT',m.n); break
    r=parse_k(m)
    if r is not None:
        if prev is not None:
            p=succ(*prev)
            if p!=r:
                bad+=1; print('MISMATCH at',m.n,prev if len(str(prev))<200 else '...',r if len(str(r))<200 else '...',p if len(str(p))<200 else '...')
                if bad>5: break
        prev=r; cnt+=1
        ds,a,b=r
        if all(d==0 for d in ds): kinds[len(ds)]=kinds.get(len(ds),0)+1
print('steps',m.n,'family configs',cnt,'mismatches',bad,'last',str(prev)[:150],'all-zero list events (len:count)',kinds)
