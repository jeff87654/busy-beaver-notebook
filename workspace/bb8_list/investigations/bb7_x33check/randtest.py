import idle, random, sys
from rules import *
random.seed(int(sys.argv[1])); N=int(sys.argv[2]); m = X if sys.argv[3]=='X' else I
cfgs=[]
for _ in range(N):
    n=random.randint(1,8)
    ds=[random.choice([0,0,1,2,random.randint(0,60)]) for _ in range(n)]
    if random.random()<0.5: ds[-1]=0
    if random.random()<0.3: ds += [0]*random.randint(1,12)
    ds[0]=max(ds[0],1) if random.random()<0.8 else ds[0]
    k=0
    while k<len(ds) and ds[-1-k]==0: k+=1
    b=random.choice([random.randint(1,30), random.randint(2*k-3 if k else 1, 2*k+40), random.randint(1,3000)])
    b=max(b,1)
    cfgs.append((ds,b))
res=literal(m,cfgs)
bad=0
for (ds,b),r in zip(cfgs,res):
    pr=predict(ds,b)
    ok = (pr[0]==r[0]) and ((pr[0]=='HALT' and pr[1]==r[1]) or (pr[0]=='K' and pr[1]==r[1] and pr[2]==r[2]))
    k=0
    while k<len(ds) and ds[-1-k]==0: k+=1
    if not ok:
        bad+=1; print('MISS', ds, b, 'k=',k, 'pred', pr, 'lit', r)
print('total',N,'bad',bad)
