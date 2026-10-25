import sys, threading, os
threading.Timer(60, lambda: os._exit(3)).start()
import lit
from lit import parse
TMS=sys.argv[1]; N=int(sys.argv[2])
t=parse(TMS);tape={};p=0;q=0
def gaps():
    ones=sorted(tape); return [ones[i+1]-ones[i]-1 for i in range(len(ones)-1)]
def comp(g):
    out=[];i=0
    while i<len(g):
        j=i
        while j<len(g) and g[j]==g[i]: j+=1
        out.append(f"{g[i]}^{j-i}" if j-i>1 else str(g[i]));i=j
    return " ".join(out)
lo=0;last=None;cnt=0
for n in range(N):
    r=t[(q,tape.get(p,0))]
    if r is None: print("halt/undef at",n,"ABCDEFGH"[q],tape.get(p,0),"ones",len(tape));break
    w,d,ns=r
    if w: tape[p]=1
    else: tape.pop(p,None)
    p+=d;q=ns
    if p<lo:
        lo=p
        if q==0:
            g=gaps(); k=2
            while k<len(g) and g[k]==1: k+=1
            key=comp(g[k:])
            if key!=last and cnt<40: print(n,k-1,key);last=key;cnt+=1
