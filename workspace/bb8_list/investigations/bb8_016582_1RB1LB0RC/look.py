from sim import *
import sys
n=int(sys.argv[1])
tape={};p=0;q='A';st=0;lo=hi=0
while st<n:
    s=tape.get(p,0);t=T[(q,s)]
    if t is None: print("HALT",st);break
    w,d,nq=t;tape[p]=w;p+=1 if d=='R' else -1;q=nq;st+=1
    if p<lo or p>hi:
        lo=min(lo,p);hi=max(hi,p)
        print(st,fmt(tape,p,q))
