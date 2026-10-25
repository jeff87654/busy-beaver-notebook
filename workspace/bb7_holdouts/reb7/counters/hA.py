import idle, random, sys
from thr import rlg
M,O,Q,S=sys.argv[1:5]; n=int(sys.argv[5]); seed=int(sys.argv[6]) if len(sys.argv)>6 else 3
random.seed(seed); H=0
for it in range(n):
    L=random.randint(1,6)
    bits=''
    for j in range(L):
        bits+='10'*random.randint(0,6)
        bits+=random.choice('0001')
    bits+='10'*random.randint(0,12)
    o=rlg(M,O,Q,'10','0',S,'P:'+bits+(' 0' ),2*10**6,1,3)
    if o[0].startswith('H'): H+=1; print('HALT',bits,o[0])
print('halts',H,'of',n)
