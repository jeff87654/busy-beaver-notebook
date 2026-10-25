from lit import *
import sys
t=parse(TM);tape={};p=0;q=0
N=int(sys.argv[1])
def gaps():
    ones=sorted(tape)
    return [ones[i+1]-ones[i]-1 for i in range(len(ones)-1)]
lo=0;last=None
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
            j=1
            while j<len(g) and g[j]==1: j+=1
            # canonical = (j-1) pairs
            rest=g[j:]
            # take rows where a>=... print all j resets: rows where rest[0] large-ish? print rows where previous a increased
            key=tuple(rest[1:])
            if key!=last: print(n,"j=",j-1,"a=",rest[0] if rest else None,"|",rest[1:]); last=key
