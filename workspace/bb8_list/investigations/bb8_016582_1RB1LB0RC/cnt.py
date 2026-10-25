from sim import *
import sys,re
a=int(sys.argv[1]);b=int(sys.argv[2])
tape={};p=0;q='A';st=0;lastd=None;lastc=None
while st<b:
    s=tape.get(p,0);t=T[(q,s)]
    w,d,nq=t
    if st>=a and q=='F' and lastd=='L' and d=='R':
        f=fmt(tape,p,q)
        m=re.match(r'(0*)((?:110)*)(.*)$',f)
        c=len(m.group(2))//3
        if c!=lastc: print(st,c,m.group(1)+' '+m.group(2)+' '+m.group(3)); lastc=c
    lastd=d
    tape[p]=w;p+=1 if d=='R' else -1;q=nq;st+=1
