import sys
from sim import *
from rl import rle
n=int(sys.argv[1]);st=sys.argv[2]
tape={};pos=0;q=0
lo=0
for i in range(n):
    b=tape.get(pos,0);e=T[(q,b)]
    if e is None: print('HALT',i);break
    w,d,nq=e
    tape[pos]=w;pos+=d;q=nq
    if pos<lo:
        lo=pos
    if pos<=lo+int(sys.argv[3]) and chr(65+q) in st:
        pass
