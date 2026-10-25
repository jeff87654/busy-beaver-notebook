from batch import *
cfgs=[]
for a in range(0,10):
    for r in (2,5):
        cfgs.append(([a],r))
        cfgs.append(([1,a],r))
res=run(cfgs,tail='111001',N=3000000)
for t,r,x in res:
    print(t,r,'->',x[1:] if isinstance(x,tuple) else x)
