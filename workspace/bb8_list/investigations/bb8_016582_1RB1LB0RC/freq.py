from sim import *
import collections
tape={};p=0;q='A';st=0;c=collections.Counter()
N=330503
while st<N:
    s=tape.get(p,0);t=T[(q,s)]
    c[q+str(s)]+=1
    w,d,nq=t;tape[p]=w;p+=1 if d=='R' else -1;q=nq;st+=1
print(sorted(c.items(),key=lambda x:x[1]))
