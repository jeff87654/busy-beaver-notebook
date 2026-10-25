import idle, random, sys
from nx import nxt,M1,M2
from model import enc, step
random.seed(int(sys.argv[1]))
tests=[]
for _ in range(int(sys.argv[2])):
    m=random.choice('HD'); k=random.randint(0,20); b=k+1+random.choice([0,0,1,2,random.randint(0,30)])
    pre=[random.choice([0,1,2,random.randint(0,12)]) for _ in range(random.randint(0,4))]
    x=random.choice([1,1,2,random.randint(1,12)])
    tests.append((m,pre+[x]+[0]*k,0,b))
    n=random.randint(1,14); b=n+random.choice([0,0,1,2,random.randint(0,30)])
    tests.append(('H',[0]*(n-1),0,b))
    tests.append(('H',[0]*(n-1),random.randint(1,5),random.randint(0,20)))
    tests.append(('S',[],0,random.randint(4,90)))
    tests.append(('O',[],0,random.randint(0,30)))
bad=0;cnt={}
for M in (M1,M2):
  for st in tests:
    pr=step(st)
    if pr[0]=='OUT': cnt['OUT']=cnt.get('OUT',0)+1; continue
    e=nxt(M,enc(st),steps=2*10**7)
    ok = e[0]=='E' and e[1]==enc(pr)
    kind='R1' if st[2]>0 else st[0]+('E' if st[0]=='H' and not any(st[1]) else '')
    cnt[kind]=cnt.get(kind,0)+1
    if not ok:
        bad+=1
        if bad<20: print('MISMATCH',M[-6:],st,'model',pr,'lit',e)
print('tested',cnt,'bad',bad)
