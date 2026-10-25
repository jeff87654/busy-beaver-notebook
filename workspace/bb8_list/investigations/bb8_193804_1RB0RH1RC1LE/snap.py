import sys
from sim import *
from rl import rle
n=int(sys.argv[1]);k=int(sys.argv[2])
tape={};pos=0;q=0
step=n//k
for i in range(n):
    b=tape.get(pos,0);e=T[(q,b)]
    if e is None: print('HALT',i);break
    w,d,nq=e
    tape[pos]=w;pos+=d;q=nq
    if i%step==0: print(i,rle(tape,pos,q))
