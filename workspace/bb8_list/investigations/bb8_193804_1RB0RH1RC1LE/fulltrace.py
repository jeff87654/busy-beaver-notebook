import sys
from sim import *
from rl import rle
from fam import build
a=int(sys.argv[1]);cs=tuple(int(x) for x in sys.argv[3:]);N=int(sys.argv[2])
s=build(a,cs)
tape={i:int(ch) for i,ch in enumerate(s)}
pos=0;q=1
def line(i):
    lo=min(tape); hi=max(tape)
    lo=min(lo,pos);hi=max(hi,pos)
    t=''
    for p in range(lo,hi+1):
        if p==pos: t+='['+chr(65+q)+']'
        t+=str(tape.get(p,0))
    return '%4d %s  (pos %d)'%(i,t,pos)
print(line(0))
for i in range(1,N+1):
    b=tape.get(pos,0);e=T[(q,b)]
    if e is None: print('HALT',i);break
    w,d,nq=e
    tape[pos]=w;pos+=d;q=nq
    print(line(i))
