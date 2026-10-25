import idle, random, sys
from nx import nxt,M1,M2
from model import enc, step
random.seed(int(sys.argv[1]) if len(sys.argv)>1 else 1)
bad=0; cnt={}
def rnd():
    m=random.choice('HD')
    L=random.randint(0,6)
    ds=[random.choice([0,0,1,2,random.randint(0,9)]) for _ in range(L)]
    a=random.choice([0,0,1,random.randint(0,8)])
    b=random.randint(0,14)
    return (m,ds,a,b)
tests=[]
for _ in range(1500): tests.append(rnd())
for b in range(4,40): tests.append(('S',[],0,b)) if b%2 else None
for b in range(0,10): tests.append(('O',[],0,b))
for M in (M1,M2):
  for st in tests:
    pr=step(st)
    if pr[0] in ('OUT',): continue
    e=nxt(M,enc(st),steps=3*10**6)
    if pr[0]=='HALT':
        ok = e[0]=='H'
    else:
        ok = e[0]=='E' and e[1]==enc(pr)
    kind = 'HALT' if pr[0]=='HALT' else ('R1' if st[2]>0 else st[0])
    cnt[kind]=cnt.get(kind,0)+1
    if not ok:
        bad+=1
        if bad<30: print('MISMATCH',M[-6:],st,enc(st),'model',pr,enc(pr) if pr[0]!='HALT' else '', 'lit',e)
print('tested',cnt,'bad',bad)
