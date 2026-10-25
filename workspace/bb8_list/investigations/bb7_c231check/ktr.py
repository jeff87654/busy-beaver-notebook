import idle,sys
from rsim import *
from rle import *
w=int(sys.argv[1]); a=int(sys.argv[2]); ds=eval(sys.argv[3]); evs=sys.argv[4].split(',')
M=M1 if w==1 else M2
r=kconfig(M,a,ds)
def render(r):
    L=r.L; R=r.R
    s=' '.join(f'{b}^{c}' for b,c in L)+f' <{"ABCDEFG"[r.s]}>{r.h} '+' '.join(f'{b}^{c}' for b,c in R[::-1])
    return s
last=None
while r.steps<10**8:
    ev='ABCDEFG'[r.s]+str(r.h)
    if ev in evs: print(r.steps, render(r))
    if not r.step(): print('HALT',r.steps,render(r)); break
    if r.s==4 and r.h==0 and not r.L and parse_k(r) and r.steps>0: print('K',r.steps,parse_k(r)); break
