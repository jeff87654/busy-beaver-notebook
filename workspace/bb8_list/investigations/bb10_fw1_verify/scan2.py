import sys
from fw import *
from hs import literal_next
P=[6,6,3]
Y=int(sys.argv[1]); w=int(sys.argv[2])
for A in [int(x) for x in sys.argv[3].split(',')]:
  for T in [int(x) for x in sys.argv[4].split(',')]:
    L=P+[Y,T,0]+[1]*w
    k,L2,A2,st,evs=literal_next(L,A,10**9)
    print('A=%d T=%d'%(A,T), '[%s | %d] ->'%(fmt(L),A), k, ('[%s | %d]'%(fmt(L2),A2)) if k=='B' else show(L2)[:200], st, 'E0=%d'%len(evs), flush=True)
