from sim import *
import sys
a=int(sys.argv[1]);b=int(sys.argv[2])
tape={};p=0;q='A';st=0;lastd=None
while st<b:
    s=tape.get(p,0);t=T[(q,s)]
    if t is None: print("HALT",st);break
    w,d,nq=t
    if st>=a and d!=lastd: print(st,fmt(tape,p,q))
    lastd=d
    tape[p]=w;p+=1 if d=='R' else -1;q=nq;st+=1
