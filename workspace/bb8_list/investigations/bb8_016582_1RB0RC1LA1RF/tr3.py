from lit import *
import sys
t=parse(TM);tape={};p=0;q=0
lo=0;N=int(sys.argv[1]);cnt=0
def gaps():
    ones=sorted(tape)
    return [ones[i+1]-ones[i]-1 for i in range(len(ones)-1)]
def comp(g):
    out=[];i=0
    while i<len(g):
        j=i
        while j<len(g) and g[j]==g[i]: j+=1
        out.append(f"{g[i]}^{j-i}" if j-i>1 else str(g[i]));i=j
    return " ".join(out)
last=None
for n in range(N):
    r=t[(q,tape.get(p,0))]
    if r is None: print("halt",n);break
    w,d,ns=r
    if w: tape[p]=1
    else: tape.pop(p,None)
    p+=d;q=ns
    if p<lo:
        lo=p
        if q==0:
            g=gaps()
            # strip the leading [0,1^k] prefix
            k=2
            while k<len(g) and g[k]==1: k+=1
            key=comp(g[k:])
            if key!=last: print(n,k-1,key); last=key
