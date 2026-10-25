import sys
from tr import *
n=int(sys.argv[1]); b=int(sys.argv[2]); thr=int(sys.argv[3])
D=lambda m:'10'*m+'1'
w='11'+D(1)*(n+1)+'10'*(3*b+2)+'111001'
t=parse(M); tp={i:int(c) for i,c in enumerate(w)}; p=len(w); q=1; lo=0; hi=len(w)-1
m2='10'*(6*b+4)+'0111'+'001'*(n+3); m3s=None
dirn=0; start=p; last=0; seen=False
for st in range(1,40000):
    c=tp.get(p,0); tr=t[(q,c)]; p0=p
    tp[p]=tr[0]; p+=tr[1]; q=tr[2]; lo=min(lo,p); hi=max(hi,p)
    d=tr[1]
    if dirn!=0 and d!=dirn:
        if abs(p0-start)>=thr:
            s=''.join(str(tp.get(i,0)) for i in range(lo,hi+1)).strip('0')
            if st>=36*b*b+252*b+166+n*(48*b+36):
                seen=True
                print(st,chr(65+q),p-lo, rle([tp.get(i,0) for i in range(lo,hi+1)],0,hi-lo)[:190])
        start=p0
    dirn=d
    if seen and q==1 and p>=hi and tp.get(p,0)==0 and st>2000: break
