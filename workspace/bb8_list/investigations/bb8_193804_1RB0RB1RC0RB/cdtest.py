import sys, random, itertools
from dig import step
def run_until(L,R,target,maxn=10**6):
    for i in range(maxn):
        if (L,R)==target: return i
        r,L,R=step(L,R)
        if r.startswith('STUCK'): return 'STUCK:'+r+' '+str((L,R))
    return 'LIMIT'
random.seed(1)
res={}
for Q in [[1,1],[0,1,1],[1,0,1,1],[0,0,1,1],[1,1,1],[0,1],[1],[0,0],[0,0,0],[1,0],[1,0,0]]:
  for x in range(4):
    for n in range(0,4):
      for D in itertools.product(range(4),repeat=n):
        D=list(D); T=[2,1]
        L=[1,0,1,1]+Q; R=[3,x]+D+[1]+T
        tgt=([1,0,1,1]+Q+[1],[0]+[3]*(len(D)+1)+[1]+T)
        out=run_until(L,R,tgt)
        res.setdefault((tuple(Q)),[]).append((x,tuple(D),out))
for Q,v in res.items():
    ok=sum(1 for x in v if isinstance(x[2],int))
    print(Q, ok,'/',len(v), [ (x,D,o) for x,D,o in v if not isinstance(o,int)][:4])
