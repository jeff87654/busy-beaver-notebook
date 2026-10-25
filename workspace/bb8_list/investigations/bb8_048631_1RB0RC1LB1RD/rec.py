import sys
sys.path.insert(0,'.')
from sim1 import T
tape={};pos=0;q=0
mx=0
n=int(sys.argv[1])
for step in range(n):
    s=tape.get(pos,0)
    t=T[(q,s)]
    w,d,nq=t
    tape[pos]=w
    pos+=1 if d=='R' else -1
    q=nq
    if pos>mx:
        mx=pos
        lo=min(tape);
        print(step+1,'ABCDEFGH'[q],mx,''.join(str(tape.get(i,0)) for i in range(lo,mx+1)),'lo',lo)
