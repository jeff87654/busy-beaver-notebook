import sys, random, itertools
from dig import step
def run_until(L,R,target,maxn=10**7):
    for i in range(maxn):
        if (L,R)==target: return i
        r,L,R=step(L,R)
        if r.startswith('STUCK'): return 'STUCK:'+r+' '+str((L,R))
    return 'LIMIT'
for P in [[],[1],[0],[1,1],[0,1],[1,0],[0,0],[1,0,1],[0,0,0]]:
  out=[]
  for j in range(1,7):
    for T in [[0],[1],[2],[3],[0,1]]:
      L=[1,0,1,0,1]+P+[1]; R=[0]+[3]*j+[1]+T
      tgt=([1,0,1,0,1]+P+[1,1,1],[0]+[3]*(j-1)+[1]+T)
      o=run_until(L,R,tgt); out.append(o if isinstance(o,int) else 'X')
  print(P,out)
