import sys,random
from randlist import run
from phi import phi
random.seed(int(sys.argv[1]))
ok=bad=0
badl=[]
for trial in range(int(sys.argv[2])):
    a=random.choice([2,2,3,3,3]+list(range(4,26)))
    k=random.randint(0,12)
    ts=tuple(random.choice([1,1,1,2,2,2,2,3,4,5,6,9,14,25]) for _ in range(k))
    r=run(a,ts,200000000)
    if r[0]!='std': bad+=1; badl.append((a,ts,r)); continue
    if r[1]==phi(a,ts): ok+=1
    else: bad+=1; badl.append((a,ts,r[1],phi(a,ts)))
print('ok',ok,'bad',bad)
for b in badl[:10]: print(b)
