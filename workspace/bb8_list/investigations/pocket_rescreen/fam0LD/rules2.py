import sys,random
from probe import step
from rules import pred
M=sys.argv[1]; random.seed(int(sys.argv[2])); bad=0; n=0
for t in range(int(sys.argv[3])):
    k=random.randint(2,8)
    Y=[random.choice([0,1,2,3]) for _ in range(random.randint(0,3))]+[0]*k+[random.choice([0,1,1,2]) for _ in range(random.randint(0,4))]
    L=[random.randint(0,400),random.choice([0,0,random.randint(1,300)])]+Y
    if random.random()<0.15: L=[random.randint(100,900)]
    p=pred(L); s=step(L,M,maxn=10**7); n+=1
    got='H' if s[0]=='H' else (s[1] if s[0]=='K' else s)
    if got!=p:
        bad+=1
        if bad<=6: print('MISMATCH',L[:10],'pred',p if p=='H' else p[:10],'got',got if not isinstance(got,list) else got[:10])
print('tested',n,'bad',bad)
