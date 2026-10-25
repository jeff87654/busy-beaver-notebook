import idle, sys
from thr import rlg
from trace_check import expand
from absNB import astep
M,O,Q,SS=sys.argv[1:5]
sts=[]
for l in rlg(M,O,Q,'10','1',SS,'B',int(sys.argv[5]) if len(sys.argv)>5 else 2*10**9,100000,1):
    if l.count('|')<2: continue
    _,P,r=l.split('|',2); r=expand(r.split())
    if P.strip()!='-' or len(r)<3 or r[0]!=1 or r[-2]!=1 or r[-1]%2 or any(x%4!=1 for x in r[1:-1]): continue
    s=(tuple((x-1)//4 for x in r[1:-2]),r[-1])
    if not sts or sts[-1]!=s: sts.append(s)
ok=bad=0
for x,x2 in zip(sts,sts[1:]):
    if astep(*x)==x2: ok+=1
    else: bad+=1; print('BAD',x,astep(*x),x2)
print('events',len(sts),'ok',ok,'bad',bad, 'last',str(sts[-1])[:80])
