import sys
from fw import *
from hs import literal_next
P=[6,6,3]
Y=int(sys.argv[1]); A=int(sys.argv[2]); w=int(sys.argv[3])
for T in range(int(sys.argv[4]), int(sys.argv[5])):
    L=P+[Y,T,0]+[1]*w
    k,L2,A2,st,evs=literal_next(L,A,10**9)
    print('T=%d'%T, '[%s | %d] ->'%(fmt(L),A), k, ('[%s | %d]'%(fmt(L2),A2)) if k=='B' else show(L2)[:200], st, 'E0=%d'%len(evs), flush=True)
