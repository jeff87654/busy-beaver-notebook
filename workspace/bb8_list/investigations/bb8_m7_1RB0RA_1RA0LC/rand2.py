from batch import *
import random, sys
random.seed(int(sys.argv[1])); n=int(sys.argv[2]); maxv=int(sys.argv[3]); N=int(sys.argv[4]); N2=int(sys.argv[5])
cfgs=[]
for _ in range(n):
    L=random.randint(1,7)
    t=[random.randint(0,maxv) for _ in range(L)]
    r=random.choice([2,5,8])
    cfgs.append((t,r))
res=run(cfgs,tail='111001',N=N)
to=[(t,r) for t,r,x in res if not isinstance(x,tuple)]
print('timeouts',len(to),flush=True)
res2=run(to[:int(sys.argv[6])],tail='111001',N=N2)
cnt={}
for t,r,x in res2:
    k='K' if isinstance(x,tuple) else x.split()[0]
    cnt[k]=cnt.get(k,0)+1
    if k=='HALT' or k=='EDGE': print(t,r,x)
    if k=='TIMEOUT': print('TO',t,r)
print(cnt)
