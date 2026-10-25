from sim import *
import sys,collections,re
N=int(sys.argv[1])
tape={};p=0;q='A';st=0
J=collections.Counter()
while st<N:
    s=tape.get(p,0);t=T[(q,s)]
    if q=='F':
        hi=max(tape)
        R=''.join(str(tape.get(i,0)) for i in range(p,hi+1)).rstrip('0')
        m=re.match(r'^(.*?)((?:00+1)*)$',R)
        gaps=[len(x)-1 for x in re.findall(r'0+1',m.group(2))]
        J[(m.group(1),tuple(gaps))]+=1
    w,d,nq=t;tape[p]=w;p+=1 if d=='R' else -1;q=nq;st+=1
seqs=collections.Counter()
for (P,g),c in J.items():
    s=re.sub(r'(2,)+', lambda mm: '2*,', ','.join(map(str,g))+',')
    seqs[s]+=1
for s,c in sorted(seqs.items(),key=lambda x:-x[1])[:60]: print(c,s)
print(len(J))
