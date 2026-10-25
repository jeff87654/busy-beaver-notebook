from absys import *
from sim import T,fmt
import sys
# real run collect F-turn strings from step a
a=int(sys.argv[1]); n=int(sys.argv[2])
tape={};p=0;q='A';st=0;real=[]
while len(real)<n+5:
    s=tape.get(p,0);t=T[(q,s)]
    if q=='F' and st>=a:
        lo=min(min(tape),p)-2;hi=max(tape)
        real.append((''.join(str(tape.get(i,0)) for i in range(lo,p)).lstrip('0'), ''.join(str(tape.get(i,0)) for i in range(p,hi+1)).rstrip('0')))
    w,d,nq=t;tape[p]=w;p+=1 if d=='R' else -1;q=nq;st+=1
# parse first real
import re
Ls,R=real[0]
L=[int(c) for c in Ls]
m=re.match(r'^(.*?)((?:00+1)*)$',R)
P=m.group(1); G=[len(x)-1 for x in re.findall(r'0+1',m.group(2))]
print('start',L,P,G)
for i in range(n):
    s=tostr(L,P,G); l2,r2=s.split('[F]')
    if (l2.lstrip('0'),r2.rstrip('0'))!=real[i]:
        print('DIFF at',i,s,real[i]); break
    L,P,G=step(L,P,G)
else: print('all match',n)
