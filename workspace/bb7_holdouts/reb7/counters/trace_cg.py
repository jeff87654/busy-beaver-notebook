import idle, sys
import absC
from thr import rlg
from trace_check import expand
# blank-tape trace check of C-map variants: args M O Q u s S delta NEWTOP TOPOFF [N]
M,O,Q,u,s,S=sys.argv[1:7]; delta=int(sys.argv[7])
if sys.argv[8]!='-': absC.NEWTOP=int(sys.argv[8])
absC.TOPOFF=int(sys.argv[9]); N=int(sys.argv[10]) if len(sys.argv)>10 else 2*10**9
sts=[]
for l in rlg(M,O,Q,u,s,S,'B',N,120,0):
    if l.count('|')<2: continue
    r=expand(l.split('|')[-1].split())
    if r[-1]==0: continue
    sts.append((r[:-2],r[-1]-delta))
ok=bad=0
for (R,y),(R2,y2) in zip(sts,sts[1:]):
    a=absC.astep(R,y)
    if a[0]==R2 and a[1]==y2: ok+=1
    else: bad+=1; print('BAD',R[:12],y,'->',str(a)[:80],'lit',R2[:12],y2)
print('ok',ok,'bad',bad)
