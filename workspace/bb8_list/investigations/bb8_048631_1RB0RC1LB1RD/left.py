import sys,re
sys.path.insert(0,'.')
from sim1 import T
tape={};pos=0;q=0
n=int(sys.argv[1]); 
cnt=0
for step in range(n):
    s=tape.get(pos,0)
    if pos==-2 and q==7:
        hi=max(k for k,v in tape.items() if v)
        st=''.join(str(tape.get(i,0)) for i in range(-2,hi+1))
        cnt+=1
        print(step,st)
    w,d,nq=T[(q,s)]
    tape[pos]=w
    pos+=1 if d=='R' else -1
    q=nq
