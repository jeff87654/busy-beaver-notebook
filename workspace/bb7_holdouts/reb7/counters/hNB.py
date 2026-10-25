import idle, random, sys
from thr import rlg
# random tapes in NOBOUNDARY language: P=101, digits (10)^r separated by '1', then a, y, S=00 ; head state Q
M,O,Q=sys.argv[1:4]; n=int(sys.argv[4]); random.seed(int(sys.argv[5]) if len(sys.argv)>5 else 1)
H=0
for it in range(n):
    L=random.randint(0,4)
    ds=[4*random.randint(0,4)+1 if random.random()<0.8 else random.randint(0,6) for _ in range(L)]
    a=4*random.randint(0,3)+1 if random.random()<0.8 else random.randint(0,5)
    y=2*random.randint(0,10) if random.random()<0.8 else random.randint(0,12)
    w='101'+''.join('10'*r+'1' for r in ds)+'10'*a+'1'+'10'*y
    o=rlg(M,O,Q,'10','1','00','P:'+w+' 0',3*10**6,2,0)
    # input "P:w 0" -> w + '' + S('00')
    if o[0].startswith('H') or (len(o)>1 and o[1].startswith('H')):
        H+=1; print('HALT',ds,a,y,o[:2])
print('halts',H,'of',n)
