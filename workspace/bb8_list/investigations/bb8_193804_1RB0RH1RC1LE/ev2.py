import sys
from sim import *
n=int(sys.argv[1])
tape={};pos=0;q=0
prev=None
lo=hi=0
log=[]
for i in range(n):
    b=tape.get(pos,0);e=T[(q,b)]
    if e is None: print('HALT',i);break
    w,d,nq=e
    log.append((i,chr(65+q),pos,b))
    tape[pos]=w;pos+=d;q=nq
# find times when head position is local minimum (turn from L to R) and record pos & state
import itertools
prevpos=None;dirs=[]
turns=[]
last=None
for k in range(1,len(log)-1):
    d1=log[k][2]-log[k-1][2]; d2=log[k+1][2]-log[k][2]
    if d1<0 and d2>0: turns.append(('min',log[k]))
    if d1>0 and d2<0: turns.append(('max',log[k]))
# print minima that are new records
rec=10**9
for t,l in turns:
    if t=='min' and l[2]<rec+0:
        rec=l[2]
        print(l)
