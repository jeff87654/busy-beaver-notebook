from batch import *
import itertools, sys
alpha=[0,1,4]
cfgs=[]
for L in range(0,6):
    for t in itertools.product(alpha,repeat=L):
        for r in (2,):
            cfgs.append((list(t)+[0],r))
res=run(cfgs,N=3000000)
def fmt(x):
    return (x[0],x[1],x[2]) if isinstance(x,tuple) else x
for t,r,x in res:
    print(t,r,'->',fmt(x))
