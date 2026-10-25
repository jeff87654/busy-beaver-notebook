from lit import *
import sys
tape={};p=0;q=0
targets=set(int(x) for x in sys.argv[1:])
for n in range(max(targets)+1):
    if n in targets:
        lo=min(tape);hi=max(tape)
        print(n,"ABCDEFGH"[q],p,lo,hi);print("".join(str(tape.get(i,0)) for i in range(lo,hi+1)))
    r=T[(q,tape.get(p,0))]
    w,d,ns=r
    if w: tape[p]=1
    else: tape.pop(p,None)
    p+=d;q=ns
