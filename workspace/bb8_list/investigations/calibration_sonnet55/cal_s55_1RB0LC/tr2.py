import sys
exec(open('ev.py').read().split("N=int")[0])
SZ=1<<22
def rl(tape,p,q,lo,hi):
    a=min(lo,p);b=max(hi,p); out=[]; i=a
    while i<=b:
        if i==p: out.append("[%s]%d"%("ABCDEFGH"[q],tape[i])); i+=1; continue
        j=i
        while j<=b and j!=p and tape[j]==tape[i]: j+=1
        out.append("%d^%d"%(tape[i],j-i) if j-i>1 else str(tape[i])); i=j
    return " ".join(out)
def trace(n,t0,t1,states,cond=None):
    tape=bytearray(SZ); p=SZ//2; q=0
    for i in range(n): tape[p+1+i]=1
    lo=p;hi=p+n
    for t in range(t1):
        if t>=t0 and "ABCDEFGH"[q] in states: yield t,rl(tape,p,q,lo,hi)
        r=tb[q*2+tape[p]]
        if r is None: yield t,"HALT"; return
        tape[p]=r[0]; p+=r[1]; q=r[2]
        lo=min(lo,p);hi=max(hi,p)
if __name__=="__main__":
    import re
    n=int(sys.argv[1]);t1=int(sys.argv[2]);st=sys.argv[3]
    prev=None
    for t,s in trace(n,0,t1,st):
        sh=re.sub(r'\^\d+','^',s)
        if sh!=prev: print(t,s)
        prev=sh
