from canon import *
import collections
L=[];P='01';G=[2]*3
C=collections.Counter()
for i in range(2000000):
    # position of each terminator relative to head: P occupies len(P) cells (head at P[0]); gaps follow
    pos=len(P) if P in ('111','011') else len(P)
    # count G[0] as starting right after P
    par=[]
    x=len(P)
    for j,g in enumerate(G):
        x+=g  # zeros
        par.append(x%2)  # position (from head) of terminator j
        x+=1
    # absolute: head position = len(L) (L includes leading zeros pushes from start) -- use len(L) parity
    key=(P, len(L)%2, tuple(sorted(set(par[1:]))), (par[0] if par else None))
    C[key]+=1
    L,P,G=step(L,P,G)
for k,v in sorted(C.items(),key=str): print(k,v)
