from canon import *
import collections,sys
L=[];P='01';G=[2]*3
C=collections.defaultdict(collections.Counter)
N=int(sys.argv[1])
for i in range(N):
    m0=0
    while m0<len(G) and G[m0]==2: m0+=1
    h0=G[m0] if m0<len(G) else -1
    C[P][(m0>0,h0 if h0<30 else 30)]+=1
    L,P,G=step(L,P,G)
for P in C: print(P,sorted(C[P].items()))
