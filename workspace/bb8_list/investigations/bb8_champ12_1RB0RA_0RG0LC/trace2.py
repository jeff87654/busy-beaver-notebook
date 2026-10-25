import sys
from fam import *
# trace to stdout: only at direction reversals, tape with run-compress of 01 pairs
tm=parse_tm(M1 if len(sys.argv)<6 else sys.argv[5])
ds=eval(sys.argv[1]); a=int(sys.argv[2]); b=int(sys.argv[3]); N=int(sys.argv[4])
w=word(ds,a,b)
size=1<<14; t=bytearray(size); p=size//2; base=p-len(w)
for i,ch in enumerate(w): t[base+i]=ord(ch)-48
q=1
import re
def comp(s):
    return re.sub(r'((?:10){3,})',lambda m:'(10)^%d'%(len(m.group(1))//2),s)
def show(t,p,q):
    lo=min(i for i in range(size) if t[i]); hi=max(i for i in range(size) if t[i])
    lo=min(lo,p); hi=max(hi,p)
    s=''.join(str(t[i]) for i in range(lo,hi+1))
    return comp(s[:p-lo])+'['+'ABCDEFGH'[q]+']'+comp(s[p-lo:])
lastd=0
for st in range(1,N+1):
    r=tm[(q,t[p])]
    if r is None: print('HALT',st); break
    w_,d,nq=r
    if d!=lastd:
        print(st-1,show(t,p,q))
    lastd=d
    t[p]=w_; p+=d; q=nq
print('end',show(t,p,q))
