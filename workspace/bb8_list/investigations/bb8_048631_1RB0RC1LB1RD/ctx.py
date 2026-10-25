import sys
from collections import Counter
from sim1 import T
tape={};pos=0;q=0
n=int(sys.argv[1])
cnt=Counter(); prevq=None
def win(p,l,r): return ''.join(str(tape.get(i,0)) for i in range(p-l,p))+'['+str(tape.get(p,0))+']'+''.join(str(tape.get(i,0)) for i in range(p+1,p+1+r))
for step in range(n):
    s=tape.get(pos,0)
    if q==2 and s==1:
        cnt[(prevq,win(pos,4,4))]+=1
    w,d,nq=T[(q,s)]
    prevq=q
    tape[pos]=w; pos+=1 if d=='R' else -1; q=nq
for k,v in sorted(cnt.items(), key=lambda kv:-kv[1])[:60]: print(k,v)
print(len(cnt))
