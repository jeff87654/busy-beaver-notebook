import random,sys
from randlist import run
from phi import phi
random.seed(5)
bad=[]
tot=0
for trial in range(400):
    a=random.choice([2,3])
    m=random.randint(13,30)
    P=tuple(random.choice([1,2]) for _ in range(m))
    for tail in [(),(30,)]:
        ts=P+tail
        r=run(a,ts,300000000)
        tot+=1
        if r[0]!='std' or r[1]!=phi(a,ts): bad.append((a,P,tail,r[:2],phi(a,ts)))
print(tot,len(bad))
for b in bad[:12]: print(b)
