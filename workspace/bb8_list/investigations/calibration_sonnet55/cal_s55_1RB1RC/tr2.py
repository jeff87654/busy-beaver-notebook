import sys
from sim import *
import itertools
def rle(s):
    return ' '.join(f"{k}{len(list(g))}" for k,g in itertools.groupby(s))
a0,a1=int(sys.argv[1]),int(sys.argv[2])
tape={};pos=0;q=0
for st in range(a1):
    if st>=a0:
        L=min(tape);H=max(tape)
        s=''.join(str(tape.get(i,0)) for i in range(min(L,pos),max(H,pos)+1))
        p=pos-min(L,pos)
        print(st,'ABCDEFGH'[q],p,rle(s[:p])+' ['+s[p:p+1]+'] '+rle(s[p+1:]))
    t=T[(q,tape.get(pos,0))]
    tape[pos]=t[0]; pos+=1 if t[1]=='R' else -1; q=t[2]
