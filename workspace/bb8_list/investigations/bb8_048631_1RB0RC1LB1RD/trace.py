import sys,re
sys.path.insert(0,'.')
from sim1 import T
tape={};pos=0;q=0
n=int(sys.argv[1]); a=int(sys.argv[2]); b=int(sys.argv[3])
prevdir=0; 
for step in range(n):
    s=tape.get(pos,0)
    w,d,nq=T[(q,s)]
    tape[pos]=w
    npos=pos+(1 if d=='R' else -1)
    dd=1 if d=='R' else -1
    if prevdir!=0 and dd!=prevdir and a<=step<=b:
        lo=min(tape);hi=max(tape)
        st=''.join(str(tape.get(i,0)) for i in range(-2,hi+3))
        # mark head
        print(step+1,'turn at',pos,'state','ABCDEFGH'[q],'->','ABCDEFGH'[nq])
    prevdir=dd
    pos=npos;q=nq
