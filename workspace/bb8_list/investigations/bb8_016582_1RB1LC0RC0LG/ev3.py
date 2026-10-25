from lit import *
import sys, itertools
N=int(sys.argv[1]);K=int(sys.argv[2])
tape={};p=0;q=0;hi=0;last=0
def blocks(lo,hi):
    s="".join(str(tape.get(i,0)) for i in range(lo,hi+1))
    return [len(x) for x in s.split("0")] 
for n in range(N):
    if p>hi:
        hi=p
        if n-last>K:
            print(n,"ABCDEFGH"[q],p,blocks(min(tape),max(tape)))
        last=n
    r=T[(q,tape.get(p,0))]
    w,d,ns=r
    if w: tape[p]=1
    else: tape.pop(p,None)
    p+=d;q=ns
