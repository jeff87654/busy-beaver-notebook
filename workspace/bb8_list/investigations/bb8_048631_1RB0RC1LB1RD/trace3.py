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
        st=''.join(str(tape.get(i,0)) for i in range(0,hi+2))
        # pair notation with head marker
        out=''
        for i in range(0,len(st)):
            if i==pos: out+='['+'ABCDEFGH'[q]+']'
            out+=st[i]
            if i%2==1: out+=' '
        print(step,out)
    prevdir=dd
    tape[pos]=w
    pos+=dd
    q=nq
