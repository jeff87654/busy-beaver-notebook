import sys
from lit import parse,M
t=parse(M);tape={};p=0;s=0;lo=0;hi=0
N=int(sys.argv[1]);out=0
for k in range(N):
    v=tape.get(p,0);r=t[(s,v)]
    if r is None: print("HALT",k);break
    tape[p]=r[0];p+=1 if r[1]=='R' else -1;s=r[2]
    if p<lo:
        lo=p
        st=''.join(str(tape.get(i,0)) for i in range(lo,max(tape)+1))
        print(k+1,'ABCDEFGH'[s],st)
    hi=max(hi,p)
