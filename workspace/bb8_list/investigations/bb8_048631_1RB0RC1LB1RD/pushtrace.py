import sys
from sim1 import T
from randlist import build
a=int(sys.argv[1]); ts=tuple(int(x) for x in sys.argv[2].split(',') if x); lo=int(sys.argv[3]); hi_s=int(sys.argv[4])
tape={}
for i,ch in enumerate(build(a,ts)):
    if ch=='1': tape[i]=1
pos=-2;q=7;prevdir=0
for step in range(hi_s):
    s=tape.get(pos,0)
    w,d,nq=T[(q,s)]
    dd=1 if d=='R' else -1
    if prevdir!=0 and dd!=prevdir and step>=lo:
        hi=max([k for k,v in tape.items() if v]+[pos])
        st=''.join(str(tape.get(i,0)) for i in range(0,hi+2))
        out=''
        for i in range(len(st)):
            if i==pos: out+='['+'ABCDEFGH'[q]+']'
            out+=st[i]
            if i%2==1: out+=' '
        print(step,out)
    prevdir=dd
    tape[pos]=w; pos+=dd; q=nq
