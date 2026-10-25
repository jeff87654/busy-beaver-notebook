import idle, random, sys
from nx import nxt,M1,M2
from model import enc, step
random.seed(int(sys.argv[1]))
tests=[]
for _ in range(int(sys.argv[2])):
    m=random.choice('HD'); k=random.randint(0,45); b=k+1+random.randint(0,120)
    pre=[random.randint(0,6) for _ in range(random.randint(0,3))]
    tests.append((m,pre+[random.randint(1,9)]+[0]*k,0,b))
    n=random.randint(1,40); b=n+random.randint(0,120)
    tests.append(('H',[0]*(n-1),0,b))
    tests.append(('S',[],0,random.randint(4,300)))
    tests.append(('O',[],0,random.randint(0,150)))
bad=0;cnt=0
for M in (M1,M2):
  for st in tests:
    pr=step(st)
    if pr[0]=='OUT': continue
    e=nxt(M,enc(st),steps=5*10**7); cnt+=1
    if not (e[0]=='E' and e[1]==enc(pr)):
        bad+=1; print('MISMATCH',M[-6:],st,'model',pr,'lit',e[0])
print('tested',cnt,'bad',bad)
