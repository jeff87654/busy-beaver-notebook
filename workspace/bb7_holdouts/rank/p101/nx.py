import idle, sys
from blk import word_of, blocks
from sim import parse
M1='1RB---_1LC0LG_1RF1RD_0RF0LE_0LC1LB_1RA0RC_1LB0LE'
M2='1RB---_1LC0LG_1RF1RD_0RF0LE_0LC1LB_1RA0RC_1RB0LE'
_tr={}
def nxt(M,r,steps=10**7,Q=1):
    """next event config from block config r (head right, state B). returns ('E',r2,steps) or ('H',steps) or ('T',)"""
    tr=_tr.setdefault(M,parse(M))
    w=word_of(r); n=len(w)
    T={}
    for i,ch in enumerate(w):
        if ch=='1': T[i]=1
    p=n; q=Q; hi=n-1; lo=0
    for st in range(steps):
        c=T.get(p,0); t=tr[(q,c)]
        if t is None: return ('H',st+0)
        if t[0]: T[p]=1; hi=max(hi,p); lo=min(lo,p)
        elif c: del T[p]
        p+=t[1]; q=t[2]
        if q==Q and p>hi and not T.get(p,0):
            while hi>lo and not T.get(hi,0): hi-=1
            if p>hi and T:
                lo=min(T); 
                s=''.join('1' if T.get(i,0) else '0' for i in range(lo,hi+1))
                return ('E',blocks(s),st+1)
    return ('T',)
