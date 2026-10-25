import sys
sys.path.insert(0,'.')
from sim1 import T
tape={};pos=0;q=0
n=int(sys.argv[1])
mx=0;out=[];last=0
for step in range(n):
    s=tape.get(pos,0)
    if pos==-2 and q==7:
        out.append((step,mx,step-last)); mx=0; last=step
    w,d,nq=T[(q,s)]
    tape[pos]=w
    pos+=1 if d=='R' else -1
    q=nq
    if pos>mx: mx=pos
print(len(out))
print(' '.join('%d'%o[1] for o in out[:300]))
print(' '.join('%d'%o[2] for o in out[:100]))
