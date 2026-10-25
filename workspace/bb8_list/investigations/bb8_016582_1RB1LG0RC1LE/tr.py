from lit import *
from from_cfg import *
import sys
L,k,m,N=map(int,sys.argv[1:5])
t,p=mk(L,k,m);q=0
for n in range(N):
    print(n,rl(render(t,p,q)))
    r=T[(q,t.get(p,0))]
    if r is None: print("HALT");break
    w,d,ns=r
    if w: t[p]=1
    else: t.pop(p,None)
    p+=d;q=ns
