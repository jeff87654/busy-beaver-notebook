import idle, random, sys
from rlp import rl
import absC
from absC import astep, fmt
if len(sys.argv)>5: absC.NEWTOP=int(sys.argv[5])
M=sys.argv[1]; O=sys.argv[2]; Q=sys.argv[3]
random.seed(11); stats={}
for it in range(int(sys.argv[4])):
    L=random.randint(1,6)
    R=[1]+[random.choice([0,2,4,0,0,1,3]) for _ in range(L)]
    if R[-1]%2==1: R[-1]-=1
    y=2*random.randint(1,L+3)+1
    a=astep(R,y)
    lit=rl(M,O,Q,R+[0,y],10**7,1,0)[0]
    lh=lit.startswith('H')
    if a[0] is None: key=(a[1],'H' if lh else 'K')
    else:
        got=lit.split('|')[1].strip() if '|' in lit else lit
        key=('OK' if got==fmt(*a) else 'MISMATCH','H' if lh else 'K')
        if key[0]=='MISMATCH': print(fmt(R,y),fmt(*a),lit)
    stats[key]=stats.get(key,0)+1
    if a[0] is None and a[1] in('SMALL','SMALLTOP'):
        b=(y-1)//2
        if lh: print('HALT',fmt(R,y))
print(stats)
