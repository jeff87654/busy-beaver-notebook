from canon import *
import collections
L=[];P='01';G=[2]*3
C=collections.Counter()
def comp(G):
    out=[];i=0
    while i<len(G):
        if G[i]==2:
            j=i
            while j<len(G) and G[j]==2: j+=1
            out.append('D');i=j
        else: out.append(G[i] if G[i]<13 else 'B'); i+=1
    return tuple(out[:4])
for i in range(3000000):
    s=''.join(map(str,L)).lstrip('0')
    if len(s)<=1: C[(s,P,comp(G))]+=1
    L,P,G=step(L,P,G)
for k,v in sorted(C.items(),key=str): print(k,v)
