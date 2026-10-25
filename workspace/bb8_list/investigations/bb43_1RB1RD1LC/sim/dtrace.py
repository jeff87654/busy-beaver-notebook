# dtrace.py "<left>" Qs "<right>" maxsteps : print configs (RLE) when state D reads 1 or when head at new extreme
import sys
from psim import T, rle
L=[int(c) for c in sys.argv[1].replace(' ','')]; q=ord(sys.argv[2][0])-65; h=int(sys.argv[2][1]); R=[int(c) for c in sys.argv[3].replace(' ','')]
n=int(sys.argv[4]); filt=sys.argv[5] if len(sys.argv)>5 else 'D1'
tape={i:v for i,v in enumerate(L+[h]+R)}; pos=len(L)
for st in range(n+1):
    s=tape.get(pos,0)
    if filt=='all' or (q==3 and s==1):
        lo=min(tape);hi=max(tape)
        print(st, rle([tape.get(i,0) for i in range(lo,pos)]), f"[{'ABCD'[q]}{s}]", rle([tape.get(i,0) for i in range(pos+1,hi+1)]))
    w,d,nq=T[(q,s)]
    if nq==25: print('HALT',st+1); break
    tape[pos]=w; pos+=d; q=nq
