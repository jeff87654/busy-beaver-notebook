from lit import *
from from_cfg import mk
def cfg(tape,p):
    # canonical form: ones L | k ones | 00 | m ones? return (L,k,m) if tape matches 1^L A 1^k 00 1^m with A at p
    L=0
    while tape.get(p-1-L,0): L+=1
    if tape.get(p-1-L,0) or any(x<p-L for x in tape): return None
    k=0
    while tape.get(p+k,0): k+=1
    if tape.get(p+k) or tape.get(p+k+1): 
        if k>0 or True: pass
    m=0
    while tape.get(p+k+2+m,0): m+=1
    if any(x>p+k+1+m for x in tape): return None
    return (L,k,m)
def first_return(L,k,m,maxn=10**6):
    t,p=mk(L,k,m);q=0
    for n in range(maxn):
        r=T[(q,t.get(p,0))]
        if r is None: return ("HALT",n,q,t.get(p,0))
        w,d,ns=r
        if w: t[p]=1
        else: t.pop(p,None)
        p+=d;q=ns
        if q==0 and n>0:
            c=cfg(t,p)
            if c and c!=(L,k,m) and (c[0]==3 or (k>0 and c[0]==L+4)): return (c,n+1)
    return None
bad=0;cnt=0
for j in range(0,5):
    L=4*j+3
    for k in range(0,5):
        for m in range(0,8):
            r=first_return(L,k,m); cnt+=1
            # expected
            if k>0: exp=((L+4,k-1,m))
            elif m>=3: exp=(3,L+2,m-3)
            elif m==2: exp=(3,L+5,0)
            elif m==0: exp=(3,1,L)
            else: exp="HALT"
            got=r[0] if r else None
            if exp=="HALT":
                ok=(got=="HALT")
            else: ok=(got==exp)
            if not ok: bad+=1; print("BAD",j,k,m,exp,r)
print(cnt,"cases",bad,"bad")
