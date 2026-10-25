import sys
from sim import *
from rl import rle
from fam import build
a=int(sys.argv[1]);cs=tuple(int(x) for x in sys.argv[2:])
s=build(a,cs)
tape={i:int(ch) for i,ch in enumerate(s)}
pos=0;q=1;lo=0
print(0,rle(tape,pos,q))
for i in range(1,100000):
    b=tape.get(pos,0);e=T[(q,b)]
    if e is None: print('HALT',i);break
    w,d,nq=e
    tape[pos]=w;pos+=d;q=nq
    if pos<lo:
        lo=pos
        print(i,rle(tape,pos,q))
        if i>int(1000): break
