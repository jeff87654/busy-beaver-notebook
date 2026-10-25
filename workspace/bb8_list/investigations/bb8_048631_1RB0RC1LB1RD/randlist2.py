import sys,random
from randlist import run
from collections import Counter
random.seed(int(sys.argv[1]))
res=Counter()
bad=[]
for trial in range(int(sys.argv[2])):
    a=random.randint(2,12)
    k=random.randint(0,7)
    ts=tuple(random.choice([1,1,2,2,3,4,5,6,7,8,9,10,11]) for _ in range(k))
    r=run(a,ts,maxsteps=3000000)
    res[r[0]]+=1
    if r[0]!='std': bad.append((a,ts,r))
print(res)
for b in bad[:30]: print(b)
