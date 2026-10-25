import sys
from abrun import abs_next
def K(ds,a,b):
    w=['U']*b+['S']+['U']*a+['S']
    for d in reversed(ds): w+=['U']*d+['S']   # dn first (nearest a), ..., d1 last
    # ds is listed d1..dn ; word order after a: dn ... d1
    return w+['S']
def Kw(ds,a,b):
    w=['U']*b+['S']+['U']*a+['S']
    for d in reversed(ds): w+=['U']*d+['S']
    return w+['S']
def parse(w):
    # K-form: no V; U^b S U^a S (U^d S)* S  ; returns (ds,a,b) with ds = d1..dn
    if 'V' in w: return None
    runs=[];c=0
    for t in w:
        if t=='U': c+=1
        else: runs.append(c); c=0
    if c: return None
    # runs: b, a, dn,...,d1, 0 (final S)
    if len(runs)<3 or runs[-1]!=0: return None
    b=runs[0];a=runs[1];rest=runs[2:-1]
    return (tuple(reversed(rest)),a,b)
def advance(ds,a,b,cap=100000):
    w=Kw(ds,a,b)
    steps=0
    while True:
        w=abs_next(w)
        steps+=1
        if w is None: return None
        p=parse(w)
        if p is not None: return p,steps
        if steps>cap: return 'CAP'
def R(ds,a,b):
    ds=list(ds)
    if a>=1: return (tuple(ds),a-1,b+1)
    if not ds or all(x==0 for x in ds): return None
    if ds[-1]>=1:
        ds[-1]-=1; return (tuple(ds),b,1)
    k=0
    while ds[-1-k]==0: k+=1
    idx=len(ds)-1-k
    return (tuple(ds[:idx]+[ds[idx]-1]+[b]+[0]*(k-1)),0,1)
def R4(n,b):
    t=n//2
    if b<=1: return None
    bb=max(b,3)
    if n%2==0: return ((bb+t-1,)+(0,)*t,0,1)
    return ((t+3,)+(0,)*(bb+t-3),0,1)
if __name__=='__main__':
    import random
    bad=0;tot=0
    # R1-R3
    random.seed(1)
    for trial in range(400):
        n=random.randint(1,5)
        ds=tuple(random.choice([0,0,1,2,3]) for _ in range(n))
        a=random.choice([0,0,1,2]); b=random.randint(1,5)
        e=R(ds,a,b)
        if e is None: continue
        r=advance(ds,a,b)
        tot+=1
        if r is None or r=='CAP' or r[0]!=e:
            bad+=1; print('MISMATCH',ds,a,b,r,e)
    print('R1-R3 abstract checks',tot,'bad',bad)
    bad=0;tot=0
    for n in range(0,8):
        for b in range(2,9):
            r=advance((0,)*n,0,b,cap=10**6)
            e=R4(n,b); tot+=1
            if r is None or r=='CAP' or r[0]!=e:
                bad+=1; print('R4 MISMATCH',n,b,r,e)
    print('R4 abstract checks',tot,'bad',bad)
