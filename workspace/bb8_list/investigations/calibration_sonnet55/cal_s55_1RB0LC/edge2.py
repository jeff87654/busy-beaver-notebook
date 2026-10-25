from lit import *
import sys,re
N=int(sys.argv[1]); 
tape={};p=0;q=0
mn=0
def rl(s): return re.sub(r'1{5,}',lambda m:'1^%d'%len(m.group()),s)
for t in range(N):
    nz=[k for k,v in tape.items() if v]
    if t<40 or (nz and p<=min(nz)-1 and t%1==0):
        s=render(tape,p,q)
        print(t,rl(s))
    w,d,ns=T[(q,tape.get(p,0))]; tape[p]=w;p+=d;q=ns
