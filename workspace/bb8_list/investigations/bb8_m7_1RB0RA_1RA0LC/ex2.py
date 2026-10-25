import sys
from ex import *
n0,n1,b0,b1,N=map(int,sys.argv[1:6])
for n in range(n0,n1+1):
    for b in range(b0,b1+1):
        res=kseq([1]*(n+1),3*b+2,True,N,2)
        print('n=%d (mod4=%d) b=%d'%(n,n%4,b), ' ; '.join(('%d %s r=%d'%(r[0],rl(r[1]),r[2]) if isinstance(r,tuple) else r) for r in res) or 'NONE',flush=True)
