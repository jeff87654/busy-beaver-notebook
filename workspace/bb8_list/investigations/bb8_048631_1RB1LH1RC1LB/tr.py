from sim import *
from fam3 import F
import sys
k,r,t,N=map(int,sys.argv[1:5])
T=parse(M);st=F(k,r,t)
tape={i:int(c) for i,c in enumerate(st)};p=0;s=1;lo=0;hi=len(st)-1
prev=None;cnt=0
def show():
    x=''.join(str(tape.get(q,0)) for q in range(lo-1,hi+2))
    h=p-(lo-1)
    return x[:h]+'['+'ABCDEFGH'[s]+']'+x[h:]
for i in range(N):
    rr=T[(s,tape.get(p,0))]
    tape[p]=rr[0];p+=1 if rr[1]=='R' else -1;s=rr[2]
    lo=min(lo,p);hi=max(hi,p)
    # print at state changes for A/E/G/H etc: print whenever state not in loop
    print(i+1,show())
