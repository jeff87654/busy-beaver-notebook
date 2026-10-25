import sys, re
from cmpabs import step, norm
def rl(l):
    return re.sub(r'(01)+', lambda m: '(01)^%d '%(len(m.group())//2), re.sub(r'0{3,}',lambda m:' 0^%d '%len(m.group()),l))
l,ds='1',(0,3,3,3,1)
N=int(sys.argv[1]); a=int(sys.argv[2]); b=int(sys.argv[3])
for i in range(N):
    r,l2,d2=step(l,ds)
    if r.startswith('STUCK'): print(r,i,l,ds); break
    if a<=i<b: print(i,r.ljust(3),rl(l).rjust(60),'|',''.join(map(str,ds)))
    l,ds=norm(l2,d2)
