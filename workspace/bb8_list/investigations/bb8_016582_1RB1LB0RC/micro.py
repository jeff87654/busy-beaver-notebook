from sim import *
import sys,collections
N=int(sys.argv[1])
tape={};p=0;q='A';st=0
rules=collections.Counter(); ex={}
cur=None
while st<N:
    s=tape.get(p,0);t=T[(q,s)]
    if t is None: print("HALT");break
    if q=='F':
        if cur is not None:
            p0,lo,hi,before=cur
            after=''.join(str(tape.get(i,0)) for i in range(lo,hi+1))
            key=(before, p0-lo, after, p-lo)
            rules[key]+=1
        cur=[p,p,p,None]
        snap=dict(tape)
    w,d,nq=t;tape[p]=w;p+=1 if d=='R' else -1;q=nq;st+=1
    if cur is not None:
        cur[1]=min(cur[1],p);cur[2]=max(cur[2],p)
        if q=='F':
            cur[3]=''.join(str(snap.get(i,0)) for i in range(cur[1],cur[2]+1))
for (b,i,a,j),c in sorted(rules.items(),key=lambda x:-x[1]):
    def mk(s,k): return s[:k]+'[F]'+s[k:]
    print(c, mk(b,i),'->',mk(a,j))
