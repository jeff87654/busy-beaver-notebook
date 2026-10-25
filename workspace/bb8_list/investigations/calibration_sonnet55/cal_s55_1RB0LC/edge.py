from lit import *
import sys,re
N=int(sys.argv[1]); 
tape={};p=0;q=0;lo=0
prev=None
for t in range(N):
    if q==0 and tape.get(p-1,0)==0 and (not tape or p<=min(k for k,v in tape.items() if v)+0 or True) and all(k>=p for k,v in tape.items() if v):
        s=render(tape,p,q)
        print(t,s if len(s)<150 else re.sub(r'1{5,}',lambda m:'1^%d'%len(m.group()),s))
    w,d,ns=T[(q,tape.get(p,0))]; tape[p]=w;p+=d;q=ns
