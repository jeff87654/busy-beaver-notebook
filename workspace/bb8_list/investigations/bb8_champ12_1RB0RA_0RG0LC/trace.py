import sys
from fam import *
# trace K(ds;a;b) literal, print tape/head/state at every step where state/dir changes pattern (compressed)
tm=parse_tm(M1)
ds=eval(sys.argv[1]); a=int(sys.argv[2]); b=int(sys.argv[3]); N=int(sys.argv[4])
w=word(ds,a,b)
size=4096; t=bytearray(size); p=size//2; base=p-len(w)
for i,ch in enumerate(w): t[base+i]=ord(ch)-48
q=1
def show(t,p,q):
    lo=min(i for i in range(size) if t[i]); hi=max(i for i in range(size) if t[i])
    lo=min(lo,p); hi=max(hi,p)
    s=''.join(str(t[i]) for i in range(lo,hi+1))
    return s[:p-lo]+'['+'ABCDEFGH'[q]+']'+s[p-lo:]
print(0,show(t,p,q))
pq=None
for st in range(1,N+1):
    r=tm[(q,t[p])]
    if r is None: print('HALT',st); break
    w_,d,nq=r; t[p]=w_; p+=d; q=nq
    print(st,show(t,p,q))
