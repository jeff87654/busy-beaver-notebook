import idle, random, sys
from rules import *
# only configs inside the precondition (b >= 2k-2 for borrows), large values, long lists; plus true exhaustions
random.seed(int(sys.argv[1])); N=int(sys.argv[2]); m = X if sys.argv[3]=='X' else I
cfgs=[]
for _ in range(N):
    n=random.randint(1,36)
    ds=[random.choice([0,1,2,2,3,random.randint(0,200),random.randint(0,5000)]) for _ in range(n)]
    r=random.random()
    if r<0.5: z=random.randint(1,n); ds[n-z:]=[0]*z
    k=0
    while k<len(ds) and ds[-1-k]==0: k+=1
    lo = max(1, 2*k-2) if k else 1
    b=random.choice([lo, lo+1, random.randint(lo, lo+50), random.randint(lo, 20000)])
    if all(x==0 for x in ds): b=random.randint(1,800)
    cfgs.append((ds,b))
res=literal(m,cfgs,10**9)
bad=0; kinds={}
for (ds,b),r in zip(cfgs,res):
    pr=predict(ds,b)
    ok = (pr[0]==r[0]) and ((pr[0]=='HALT' and pr[1]==r[1]) or (pr[0]=='K' and pr[1]==r[1] and pr[2]==r[2]))
    k=0
    while k<len(ds) and ds[-1-k]==0: k+=1
    kind = 'E' if not norm(ds) else ('D' if k==0 else 'B')
    kinds[kind]=kinds.get(kind,0)+1
    if not ok: bad+=1; print('MISS', ds, b, 'k=',k, 'pred', pr, 'lit', r)
print('total',N,'bad',bad,kinds)
