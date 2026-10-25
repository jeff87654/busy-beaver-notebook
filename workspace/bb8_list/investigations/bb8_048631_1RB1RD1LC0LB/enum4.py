import sys, itertools, random
from cyc import *
from enum1 import cycle
random.seed(5)
tails=[''.join(random.choice('01') for _ in range(24))+'0'*30 for _ in range(4)]
def rule(p,n):
    """find (g, k) with R' = g + R[k:] for every tail, k>=len(p)?? minimal k over any tail-suffix match"""
    res=[]
    for t in tails:
        R=p+t
        kind,k,r,reach=cycle(n,R)
        if kind!='stop': return ('X',kind,k,reach)
        Lr,Rr,pos=r
        res.append((R,Rr,Lr,k))
    # find smallest k (index into R) such that for all tails: Rr endswith R[k:] and the prefix part identical
    for kk in range(0,len(p)+8):
        gs=set(); ok=True
        for R,Rr,Lr,_ in res:
            suf=R[kk:]
            # suffix of Rr equal to suf? compare from end
            if not Rr.endswith(suf) or len(suf)==0: ok=False;break
            gs.add(Rr[:len(Rr)-len(suf)])
        if ok and len(gs)==1:
            return (kk,gs.pop(),[len(x[2]) for x in res],res[0][3])
    return None
if __name__=='__main__':
    n=int(sys.argv[1]); Lp=int(sys.argv[2])
    for combo in itertools.product('01',repeat=Lp):
        p=''.join(combo)
        print(p,rule(p,n))
