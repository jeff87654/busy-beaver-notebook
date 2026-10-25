from sim import *
import sys,collections,re
N=int(sys.argv[1])
tape={};p=0;q='A';st=0
J=collections.Counter()
while st<N:
    s=tape.get(p,0);t=T[(q,s)]
    if q=='F':
        lo=min(tape);hi=max(tape)
        L=''.join(str(tape.get(i,0)) for i in range(lo-3,p))
        R=''.join(str(tape.get(i,0)) for i in range(p,hi+1)).rstrip('0')
        m=re.match(r'^(.*?)((?:00+1)*)$',R)
        gaps=[len(x)-1 for x in re.findall(r'0+1',m.group(2))]
        g1=gaps[0] if gaps else 'inf'
        if g1!='inf' and g1>=6: g1='6+'
        J[(L[-2:],m.group(1),g1)]+=1
    w,d,nq=t;tape[p]=w;p+=1 if d=='R' else -1;q=nq;st+=1
for k,v in sorted(J.items(),key=str): print(k,v)
