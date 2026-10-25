from batch import *
import itertools
vals=[0,1,2,3,4,5,7]
cfgs=[]
for L in (1,2):
    for t in itertools.product(vals,repeat=L):
        for r in (0,5):
            cfgs.append((list(t)+[0],r))
res=run(cfgs)
for t,r,x in res:
    print(t,r,'->',x[1:] if isinstance(x,tuple) else x)
