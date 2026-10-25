from lit import *
import sys
st=int(sys.argv[1]); N=int(sys.argv[2]); cnt=0
tape={};p=0;q=0
for t in range(N):
    if q==st:
        cnt+=1
        if cnt<=int(sys.argv[3]): print(t,render(tape,p,q))
    w,d,ns=T[(q,tape.get(p,0))]; tape[p]=w;p+=d;q=ns
print(cnt)
