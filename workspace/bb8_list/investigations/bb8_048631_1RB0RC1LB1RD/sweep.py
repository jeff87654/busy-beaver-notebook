import sys,random
from randlist import run
from phi import phi
random.seed(int(sys.argv[1]))
bad=0;tot=0
# push for large a
for a in range(4,int(sys.argv[2])):
    r=run(a,(7,),900000000)
    tot+=1
    if r[0]!='std' or r[1]!=phi(a,(7,)): bad+=1; print('PUSH BAD',a,r[:2],phi(a,(7,)))
print('push sweep',tot,'bad',bad)
# prefix rule: all (m,u) for a=2,3 with m up to M, random placements, with tail 40 and end
M=int(sys.argv[3])
for a in (2,3):
    for m in range(0,M+1):
        for u in range(0,m+1):
            pos=random.sample(range(m),u)
            P=tuple(1 if i in pos else 2 for i in range(m))
            for tail in ((40,),()):
                ts=P+tail
                r=run(a,ts,2000000000)
                tot+=1
                if r[0]!='std' or r[1]!=phi(a,ts): bad+=1; print('PREFIX BAD',a,P,tail,r[:2],phi(a,ts))
    print('a',a,'done tot',tot,'bad',bad,flush=True)
