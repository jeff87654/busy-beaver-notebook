import idle, random, sys
import absC
from absC import astep, fmt
from thr import rlg
# validate absC rules with rlg (any S); args: M O Q S n [NEWTOP]
M,O,Q,S=sys.argv[1:5]; n=int(sys.argv[5])
if len(sys.argv)>6 and sys.argv[6]!='-': absC.NEWTOP=int(sys.argv[6])
if len(sys.argv)>7: absC.TOPOFF=int(sys.argv[7])
random.seed(7); bad=tot=0
for it in range(n):
    L=random.randint(1,6)
    R=[random.choice([1,3,5,7])]+[random.choice([0,2,4,6,0,0,1,3,5]) for _ in range(L)]
    if R[-1]%2==1: R[-1]-=1
    y=2*random.randint(L+3,L+20)+1
    a=astep(R,y)
    if a[0] is None: continue
    lit=rlg(M,O,Q,'1','0',S,' '.join(map(str,R+[0,y])),10**8,1,0)[0]
    got=lit.split('|')[-1].strip() if '|' in lit else lit
    tot+=1
    if got!=fmt(*a): bad+=1; print('MISMATCH',fmt(R,y),fmt(*a),lit)
print('tot',tot,'bad',bad)
