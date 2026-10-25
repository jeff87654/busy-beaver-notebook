from batch import *
cfgs=[]
for T in (22,34,46):
    for k in range(2,12):
        for r in (2,5,8,380):
            cfgs.append(([T,21]+[1]*k+[0,0,1],r))
res=run(cfgs,tail='111001',N=2000000000)
bad=0;tot=0
for t,r,x in res:
    T=t[0];k=len(t)-5
    if not isinstance(x,tuple): print('NOK',t,r,x); bad+=1; continue
    exp=[T,21]+[1]*(k-2)+[0,1,2*r+2]; tot+=1
    if x[1]!=exp or x[2]!=2: print('MISMATCH',t,r,x[1],x[2],'exp',exp); bad+=1
print('C2->C3 check',tot,'bad',bad)
# C1 -> C2 : [T',1^m,2,0,3,3] r=2 with T'=T+3
cfgs=[]
for T in (22,34,46):
    for m in (11,23,35):
        cfgs.append(([T+3]+[1]*m+[2,0,3,3],2))
res=run(cfgs,tail='111001',N=2000000000)
for t,r,x in res:
    T=t[0]-3;m=len(t)-5
    exp=[T,21]+[1]*(m-2)+[0,0]+[19]
    print(T,m, 'ok' if isinstance(x,tuple) and x[1]==exp else ('NOK',x if not isinstance(x,tuple) else (x[1][:6],x[1][-5:],x[2],len(x[1]))), 'exp len',len(exp))
