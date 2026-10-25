import sys
TM="1RB1LG_0RC1LE_1RD1LC_0LB1RH_0LF1LB_1RF1RA_0LE0LG_---0RG"
def parse(tm):
    t={}
    for i,c in enumerate(tm.split("_")):
        for s in (0,1):
            e=c[3*s:3*s+3]
            t[(i,s)]=None if e=="---" else (int(e[0]),1 if e[1]=="R" else -1,ord(e[2])-65)
    return t
T=parse(TM)
def run(N,cb=None):
    tape={};p=0;q=0
    for n in range(N):
        if cb: cb(n,q,p,tape)
        r=T[(q,tape.get(p,0))]
        if r is None: print("halt/undef",n,q,sum(tape.values()));return tape,p,q
        w,d,ns=r
        if w: tape[p]=1
        else: tape.pop(p,None)
        p+=d;q=ns
    return tape,p,q
def render(tape,p,q):
    lo=min(min(tape,default=p),p);hi=max(max(tape,default=p),p)
    s="".join(("1" if tape.get(i,0) else "0") for i in range(lo,hi+1))
    return s[:p-lo]+"["+"ABCDEFGH"[q]+"]"+s[p-lo:]
if __name__=="__main__":
    N=int(sys.argv[1]); t,p,q=run(N); print(render(t,p,q))
