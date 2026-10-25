from batch import *
cfgs=[]
for x in (22,):
  for y in (21,):
    for k in range(0,11):
        for r in (0,5):
            cfgs.append(([x,y]+[1]*k+[0,0,1,0],r))
res=run(cfgs,N=20000000)
for t,r,x in res:
    print(t,r,'->',x[1:] if isinstance(x,tuple) else x)
