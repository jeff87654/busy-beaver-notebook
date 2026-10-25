import sys
from sim import *
a,b=int(sys.argv[1]),int(sys.argv[2])
tape={};pos=0;q=0
for st in range(1130):
    t=T[(q,tape.get(pos,0))]
    tape[pos]=t[0]; pos+=1 if t[1]=='R' else -1; q=t[2]
    if st>=1129-0 : pass
# print steps 1130..1172
for st in range(1130,1175):
    L=min(tape);H=max(tape)
    s=''.join(str(tape.get(i,0)) for i in range(L,H+1))
    # compress
    print(st,'ABCDEFGH'[q],pos-L, s[:12],'...',s[-70:])
    t=T[(q,tape.get(pos,0))]
    tape[pos]=t[0]; pos+=1 if t[1]=='R' else -1; q=t[2]
