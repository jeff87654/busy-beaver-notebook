import re
from tr import *
def kword(n,b):
    D=lambda m:'10'*m+'1'
    return '11'+D(1)*(n+1)+'10'*(3*b+2)+'111001'
pat=re.compile(r'^1010111((?:001)*)00(1+)001001$')
def find(n,b,maxs):
    w=kword(n,b); t=parse(M); tp={i:int(c) for i,c in enumerate(w)}; p=len(w); q=1; hi=len(w)-1; lo=0
    for st in range(maxs):
        c=tp.get(p,0); tr=t[(q,c)]
        tp[p]=tr[0]; p+=tr[1]; q=tr[2]; hi=max(hi,p); lo=min(lo,p)
        if q==1 and p>=hi and tp.get(p,0)==0:
            s=''.join(str(tp.get(i,0)) for i in range(lo,hi+1)).strip('0')
            m=pat.match(s)
            if m: return (st+1,len(m.group(1))//3,len(m.group(2)))
    return None
for n in range(0,5):
    print(n,[find(n,b,60000) for b in range(0,4)])
