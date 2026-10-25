import sys
from functools import lru_cache
# parity-level abstract model: CLEARDIGIT(j, v(parity vp, nonzero flag), p) -> p'
@lru_cache(None)
def BLK(j,p):
    # clear [2^(j-1); r] from b=7 (odd), r≡p, j>=1 ; returns parity
    q=1
    for i in range(j-1):
        q=CD(i,0,True,q)
    return CD(j-1,p,True,q)
@lru_cache(None)
def CD(j,vp,nz,p):
    if not nz: return p
    if j==0: return (p+vp)%2
    # iterate v times: M(p)=BLK(j,p); need v parity; v>=1
    M=lambda x:BLK(j,x)
    # compute M^v for v parity vp, v>=1: v=1 -> M, v even>=2 -> M^2, odd>=1 -> M (if vp=1, M^v for v odd = M * (M^2)^((v-1)/2)) ; careful general
    return itM(M,vp,p)
def itM(M,vp,p):
    # result of applying M v times for v>=1 with v%2==vp; maps on {0,1}; M^(v) for large v: determine via eventual behavior
    # compute M^1, M^2, M^3, M^4 ; for general v: M^v = M^(v-2k) while periodic: orbit eventually periodic with period<=2 starting at power<=2
    pw=[p]
    x=p
    pows={}
    for t in range(1,7):
        x=M(x); pows[t]=x
    # periodic from t>=2 with period 2 (maps on 2 points): M^t for t>=2 depends on t mod 2
    if vp==1:
        return pows[1] if True else None
    # vp==0, v>=2
    return pows[2]
if __name__=='__main__':
    for j in range(0,9):
        print(j,[BLK(j,p) for p in (0,1)] if j>=1 else '-', [[CD(j,vp,True,p) for p in (0,1)] for vp in (0,1)])
