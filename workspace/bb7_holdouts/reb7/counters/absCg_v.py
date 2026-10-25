import idle, random, sys
import absC
from absC import astep, fmt
from thr import rlg
# generic C-map validator: args M O Q u s S delta prefixbits('-' none) n NEWTOP('-') TOPOFF
M,O,Q,u,s,S=sys.argv[1:7]; delta=int(sys.argv[7]); pre=sys.argv[8]; n=int(sys.argv[9])
if len(sys.argv)>10 and sys.argv[10]!='-': absC.NEWTOP=int(sys.argv[10])
if len(sys.argv)>11: absC.TOPOFF=int(sys.argv[11])
random.seed(7); bad=tot=0
for it in range(n):
    L=random.randint(1,6)
    R=[random.choice([1,3,5,7])]+[random.choice([0,2,4,6,0,0,1,3,5]) for _ in range(L)]
    if R[-1]%2==1: R[-1]-=1
    y=2*random.randint(L+3,L+20)+1
    a=astep(R,y)
    if a[0] is None: continue
    inp=('P:'+pre+' ' if pre!='-' else '')+' '.join(map(str,R+[0,y+delta]))
    out=rlg(M,O,Q,u,s,S,inp,10**8,4,0)
    got=None
    for lit in out:
        if lit.count('|')<2: got=lit; break
        r=lit.split('|')[-1].split()
        if r[-1]!='0' and not r[-1].startswith('0x'): got=lit.split('|',1)[1].strip(); break
    tot+=1
    exp=fmt(a[0],a[1]+delta)
    if got is None or not got.endswith('| '+exp) and got!=exp:
        bad+=1; print('MISMATCH',fmt(R,y+delta),'exp',exp,'lit',got)
print('tot',tot,'bad',bad)
