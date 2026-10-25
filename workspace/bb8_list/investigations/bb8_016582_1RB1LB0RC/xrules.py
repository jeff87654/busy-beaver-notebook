# test rules: X(c,G): L=T^c 1, P=111, G'=(0,G).  (A) X(c,G) -> X(0,(2c,G)) ; (B) X(0,(2^j,h,R)) -> X(j+1,(h-2,R))
from canon import *
import random
def X(c,G): return [1,1,0]*c+[1],'111',[0]+list(G)
def run_until(st, target, maxn=10**7):
    L,P,G=st
    for i in range(maxn):
        L,P,G=step(L,P,G)
        if (L,P,G)==target: return i+1
        # strip leading zeros of L for comparison
        while L and L[0]==0: L=L[1:]
        if (L,P,G)==target: return i+1
    return None
bad=0
for c in range(1,9):
    for t in range(5):
        G=[random.choice([2,4,6,8,10]) for _ in range(random.randint(0,4))]
        r=run_until(X(c,G), X(0,[2*c]+G))
        if r is None: print('A fail',c,G); bad+=1
        elif t==0: print('A ok c=%d steps=%d'%(c,r))
for j in range(0,6):
    for h in [4,6,8,10]:
        R=[random.choice([2,4,6]) for _ in range(2)]
        r=run_until(X(0,[2]*j+[h]+R), X(j+1,[h-2]+R))
        if r is None: print('B fail',j,h,R); bad+=1
    r=run_until(X(0,[2]*j), X(j+1,[]))
    if r is None: print('B inf fail',j); bad+=1
print('bad',bad)
