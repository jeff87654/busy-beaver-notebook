import sys
from machines import *
from rsim import Sim
# Print at B visits, tape as block lists: a block = maximal 1-run; show cells as 1-run lengths separated by zero-run lengths
m = globals()[sys.argv[1]]; N = int(sys.argv[2]); st = sys.argv[3]; lim=int(sys.argv[4]) if len(sys.argv)>4 else 10**9
def fmt(runs):
    out=[]
    for s,n in runs:
        out.append(str(n) if s==1 else ('.'*n if n<4 else f".{n}."))
    return ' '.join(out)
s = Sim(m); cnt=0; prev=None
for i in range(N):
    if s.halted: print('HALT', s.steps); break
    if s.st in st:
        Lr = fmt(s.L); Rr = fmt(list(reversed(s.R)))
        shape = (len(s.L), len(s.R), s.st)
        if shape != prev:
            print(f"{s.steps:>10} {Lr} | {s.st}{'>' if s.face=='R' else '<'} | {Rr}"[:300]); cnt+=1
            if cnt>=lim: break
        prev = shape
    s.step()
