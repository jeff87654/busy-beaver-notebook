import sys
from seqx import *
n0,n1,b0,b1,N=map(int,sys.argv[1:6])
for n in range(n0,n1+1):
    for b in range(b0,b1+1):
        res=seq(n,b,N,maxprint=3)
        print('n=%d (mod4=%d) b=%d'%(n,n%4,b), ' ; '.join(('%d %s r=%d'%(r[0],rl(r[1]),r[2]) if isinstance(r,tuple) else r) for r in res[:3]) or 'NONE',flush=True)
