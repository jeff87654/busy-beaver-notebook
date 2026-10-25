from batch import *
bad=0;tot=0
cfgs=[]
for T in (22,34,46):
    for k in range(1,12):
        for r in (2,5,8,14):
            cfgs.append(([T,21]+[1]*k+[0,1,0],r))
res=run(cfgs,tail='111001',N=2000000000)
for t,r,x in res:
    T=t[0];k=len(t)-5
    if not isinstance(x,tuple): print('NOK',t,r,x); bad+=1; continue
    out=x[1]
    exp=[T,21]+[1]*(k-2)+[0,1,2*r+2] if k>=2 else [T,20,1,2*r+2]
    tot+=1
    if out!=exp or x[2]!=2: print('MISMATCH',t,r,out,x[2],'exp',exp); bad+=1
print('stage check',tot,'bad',bad)
cfgs=[]
for T in (22,34,46):
    for r in (2,5,8,14,20,26):
        cfgs.append(([T,20,1,0],r))
res=run(cfgs,tail='111001',N=2000000000)
bad=0;tot=0
for t,r,x in res:
    T=t[0]
    if not isinstance(x,tuple): print('NOK',t,r,x); bad+=1; continue
    exp=[T,16,2*r+3,1]; tot+=1
    if x[1]!=exp or x[2]!=2: print('MISMATCH',t,r,x[1],x[2],'exp',exp); bad+=1
print('end check',tot,'bad',bad)
