# grid68.py: literal check of the F68 engine on random constructed configs (both A parities, s>=1 sources, zero runs, D, T)
import sys,random
from lit68 import litnext
from f68eng import step,show,margin
def dep(st):
    A,L,c=st
    if L[0]>0: return None
    j=1
    while j<len(L) and L[j]==0: j+=1
    return j
def rand_cfg(rng):
    A=rng.choice([0,1,2,3,4,5,7,9,11,15,20,31,60,101])
    j=rng.choice([0,1,1,2,3,4,5,6,8,10,13,17,25])
    L=[0]*j+[rng.choice([0,1,1,2,3,5,13,40])]
    for _ in range(rng.randrange(0,4)): L.append(rng.choice([0,0,1,1,2,7]))
    if rng.random()<0.2: L[0]=rng.choice([1,2,5])
    return (A,tuple(L),-1)
if __name__=='__main__':
    N=int(sys.argv[1]); rng=random.Random(int(sys.argv[2]))
    ok=0; fails={}; okmin={}
    for it in range(N):
        st=rand_cfg(rng); pred,r=step(st); got=litnext(st,4000000)
        d=dep(st); key=(r[0] if r!='T0' else 'T0', None if d is None else (st[0]-(d-1) if r[0]=='B' else st[0]-(len(st[1])-2)))  # (rule, A - required)
        if got==pred: ok+=1; okmin[key[0]]=min(okmin.get(key[0],99),key[1] if key[1] is not None else 99)
        else: fails.setdefault(key[0],[]).append((key[1],show(st),show(pred) if pred else None,show(got) if isinstance(got,tuple) else got))
    print('tested',N,'ok',ok)
    print('min (A - (j-1)) among passing B/T cases:',okmin)
    for k,v in fails.items():
        print('FAIL',k,len(v),'max (A-(j-1)) among fails:',max(x[0] for x in v))
        for x in v[:3]: print('   ',x)
