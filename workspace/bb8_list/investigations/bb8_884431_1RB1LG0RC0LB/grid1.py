import itertools, sys
from fam import *
def pred(ds,a,b):
    ds=list(ds)
    if a>=1: return ('K',(tuple(ds),a-1,b+2))
    k=0
    while ds and ds[-1]==0: ds.pop(); k+=1   # trailing zeros
    if not ds: return ('R4?',None)
    y1=ds.pop()   # y+1
    if k==0:
        return ('K',(tuple(ds+[y1-1]),b+2,0))
    return ('K',(tuple(ds+[y1-1,b+2]+[0]*(k-1)),0,0))
bad=0;tot=0;res={}
for b in range(0,6):
  for a in range(0,3):
    for ds in itertools.chain.from_iterable(itertools.product(range(0,4),repeat=n) for n in range(1,4)):
        ds=list(ds)
        if ds[0]==0 and False: pass
        tot+=1
        r=run_next(ds,a,b,N=200000)
        p=pred(ds,a,b)
        if p[0]=='R4?':
            res[(tuple(ds),a,b)]=r[:3] ; continue
        if r[0]=='K' and r[2]==p[1]: continue
        bad+=1
        if bad<40: print('MISMATCH',ds,a,b,r[:3] if r[0]!='HALT' else r[:3],'pred',p)
print(tot,bad)
print(res)
