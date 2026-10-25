import idle, random, sys
from rlp import rl
m,O,Q=sys.argv[1:4]
random.seed(1)
res={}
for it in range(int(sys.argv[4])):
    n=random.randint(1,5)
    runs=[random.choice([0,0,1,2,2,3,4,5]) for _ in range(n)]
    if runs[0]==0: runs[0]=1
    y=2*random.randint(0,6)+1
    r=runs+[0,y]
    out=rl(m,O,Q,r,200000,1,0)
    print(' '.join(map(str,r)),'->',out[0])
