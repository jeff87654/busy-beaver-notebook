from lit import *
import sys
N=int(sys.argv[1]);tape={};p=0;q=0;ev=[];mn=10**9
lastlo=None
for n in range(N):
    r=T[(q,tape.get(p,0))]
    if r is None: print("HALT",n);break
    # event: head at leftmost 1 position (or left of it), moving in state
    if tape and p<=min(tape):
        ev.append((n,q,p,min(tape),max(tape),sum(tape.values())))
    w,d,ns=r
    if w: tape[p]=1
    else: tape.pop(p,None)
    p+=d;q=ns
prev=None
for e in ev:
    if prev is None or e[0]-prev>1: print(e)
    prev=e[0]
