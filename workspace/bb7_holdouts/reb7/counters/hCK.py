import idle, random, sys
from thr import rlg
M='1RB1RA_0LC0LD_1RE1LD_1LB1LC_1RF1RG_0RA0RA_---0RF'
random.seed(int(sys.argv[2]) if len(sys.argv)>2 else 1); H=0; n=int(sys.argv[1])
for it in range(n):
    L=random.randint(1,5)
    ds=[random.choice([0,0,1,2,3]) for _ in range(L)]
    y=random.randint(0,12)
    o=rlg(M,'L','C','11','0','1011','P:1 '+' '.join(map(str,ds+[0,y])),3*10**6,3,0)
    if any(x.startswith('H') for x in o): H+=1; print('HALT',ds,y,[x for x in o if x.startswith('H')])
print('halts',H,'of',n)
