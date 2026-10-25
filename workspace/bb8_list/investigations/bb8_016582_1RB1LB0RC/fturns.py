from sim import *
import sys,re
a=int(sys.argv[1]);b=int(sys.argv[2]); Q=sys.argv[3] if len(sys.argv)>3 else 'F'
tape={};p=0;q='A';st=0;lastd=None
while st<b:
    s=tape.get(p,0);t=T[(q,s)]
    if t is None: print("HALT",st);break
    w,d,nq=t
    if st>=a and q in Q and lastd=='L' and d=='R':
        f=fmt(tape,p,q)
        m=re.match(r'0*((?:110)*)(.*)$',f)
        print(st,len(m.group(1))//3, m.group(2))
    lastd=d
    tape[p]=w;p+=1 if d=='R' else -1;q=nq;st+=1
