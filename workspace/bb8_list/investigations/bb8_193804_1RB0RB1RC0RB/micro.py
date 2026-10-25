# record H-event to H-event rewrites over visited cells
from sim import *
import sys, re, collections
N=int(sys.argv[1]); a=int(sys.argv[2])
def rl(s):
    return re.sub(r'0{4,}',lambda m:'0{%d}'%len(m.group()),s)
seg={'start':None}
rules=collections.Counter(); ex={}
def cb(i,tape,pos,s):
    if seg['start'] is not None:
        seg['lo']=min(seg['lo'],pos); seg['hi']=max(seg['hi'],pos)
    if s=='H':
        if seg['start'] is not None and i>=a:
            lo,hi,p0,before=seg['lo'],seg['hi'],seg['p0'],seg['tape']
            B=''.join(str(before.get(p,0)) for p in range(lo,hi+1))
            A=''.join(str(tape.get(p,0)) for p in range(lo,hi+1))
            bs=B[:p0-lo]+'['+B[p0-lo]+']'+B[p0-lo+1:]
            As=A[:pos-lo]+'['+A[pos-lo]+']'+A[pos-lo+1:]
            k=rl(bs)+' -> '+rl(As)
            rules[k]+=1
            if k not in ex: ex[k]=(seg['start'],i-seg['start'])
        seg.update(start=i,lo=pos,hi=pos,p0=pos,tape=dict(tape))
run(N,cb)
for k,v in sorted(rules.items(),key=lambda x:-x[1]): print(v,ex[k],k)
