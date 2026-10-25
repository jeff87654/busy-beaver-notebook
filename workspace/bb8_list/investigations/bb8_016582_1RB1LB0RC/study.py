from canon import *
import collections,sys
def cls(v): return 'I' if v>=INF//2 else (v if v<7 else '7+')
L=[];P='01';G=[2]*3
C=collections.Counter()
N=int(sys.argv[1])
for i in range(N):
    # describe: P, g1, then after g1: run of 2 length class, next
    g1=G[0] if G else INF
    rest=G[1:]
    m=0
    while m<len(rest) and rest[m]==2: m+=1
    h=rest[m] if m<len(rest) else INF
    # also for P in 11/01: run from first
    m0=0
    while m0<len(G) and G[m0]==2: m0+=1
    h0=G[m0] if m0<len(G) else INF
    lb=''.join(map(str,([0,0,0]+L)[-2:]))
    C[(P,lb,cls(g1),min(m,2),cls(h),min(m0,2),cls(h0))]+=1
    L,P,G=step(L,P,G)
for k,v in sorted(C.items(),key=str): print(k,v)
