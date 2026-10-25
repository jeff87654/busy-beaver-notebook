import sys,re
sys.path.insert(0,'.')
from sim1 import T
tape={};pos=0;q=0
a=int(sys.argv[1]); b=int(sys.argv[2])
prevdir=0
for step in range(b):
    s=tape.get(pos,0)
    w,d,nq=T[(q,s)]
    dd=1 if d=='R' else -1
    if prevdir!=0 and dd!=prevdir and step>=a:
        hi=max([k for k,v in tape.items() if v]+[pos])
        st=''.join(str(tape.get(i,0)) for i in range(-2,hi+2))
        st=st[:pos+2]+'<'+'ABCDEFGH'[q]+'>'+st[pos+2:]
        print(step,st)
    prevdir=dd
    tape[pos]=w
    pos+=dd
    q=nq
