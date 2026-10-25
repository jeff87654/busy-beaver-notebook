import sys
from sim import *
from rl import rle
from fam import build
# print B-at-left-boundary events with RLE: events where head in B and everything to the left of head is 1^k (k>=0) preceded by blank
a=int(sys.argv[1]);cs=tuple(int(x) for x in sys.argv[2:])
s=build(a,cs)
tape={i:int(ch) for i,ch in enumerate(s)}
pos=0;q=1
import re
def full(tape,pos,q):
    lo=min(min(tape),pos);hi=max(max(tape),pos)
    t=''
    for p in range(lo,hi+1):
        if p==pos: t+='['+chr(65+q)+']'
        t+=str(tape.get(p,0))
    return t
print(0,rle(tape,pos,q))
for i in range(1,5000):
    b=tape.get(pos,0);e=T[(q,b)]
    if e is None: print('HALT',i);break
    w,d,nq=e
    tape[pos]=w;pos+=d;q=nq
    if q==1:
        t=full(tape,pos,q)
        left=t.split('[B]')[0]
        if re.fullmatch(r'1*',left) :
            print(i,rle(tape,pos,q))
