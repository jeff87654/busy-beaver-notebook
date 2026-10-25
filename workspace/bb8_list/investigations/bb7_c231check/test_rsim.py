import idle
from rsim import *
r=RSim(M1,[],0,[],0)
hits=[]
def isk(r):
    return r.s==4 and r.h==0 and not r.L
while r.steps<200000:
    if r.run_until(isk,200000)!='HIT': break
    k=parse_k(r)
    if k: print(r.steps,k[0],len(k[1]),k[1][:3])
