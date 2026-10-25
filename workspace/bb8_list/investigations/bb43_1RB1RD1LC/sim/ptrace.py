# ptrace.py "<left>" Qs "<right>" maxsteps P : print configs (RLE) when head position (index from left marker) <= P
import sys
from psim import T, rle
L=[int(c) for c in sys.argv[1].replace(' ','')]; q=ord(sys.argv[2][0])-65; h=int(sys.argv[2][1]); R=[int(c) for c in sys.argv[3].replace(' ','')]
n=int(sys.argv[4]); P=int(sys.argv[5])
tape={i:v for i,v in enumerate(L+[h]+R)}; pos=len(L)
for st in range(n+1):
    s=tape.get(pos,0)
    if pos<=P:
        lo=min(tape);hi=max(tape)
        sys.stdout.write("%d %s [%s%d] %s\n"%(st, rle([tape.get(i,0) for i in range(lo,pos)]), 'ABCD'[q], s, rle([tape.get(i,0) for i in range(pos+1,hi+1)])))
    w,d,nq=T[(q,s)]
    if nq==25: print('HALT',st+1); break
    tape[pos]=w; pos+=d; q=nq
