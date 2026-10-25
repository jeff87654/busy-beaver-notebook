import sys
TM="1RB0RC_1LA1RF_0RE0LD_1LE0LH_1LA0LG_1RA0LF_0LC1LE_---1LF"
def parse(tm):
    t={}
    for i,c in enumerate(tm.split("_")):
        for s in (0,1):
            e=c[3*s:3*s+3]
            t[(i,s)]=None if e=="---" else (int(e[0]),1 if e[1]=="R" else -1,ord(e[2])-65)
    return t
def run(N,show=[]):
    t=parse(TM);tape={};p=0;q=0;out=[]
    for n in range(N):
        if n in show: out.append((n,q,p,dict(tape)))
        r=t[(q,tape.get(p,0))]
        if r is None: print("halt/undef",n,q,tape.get(p,0),sum(tape.values()));return out
        w,d,ns=r
        if w: tape[p]=1
        else: tape.pop(p,None)
        p+=d;q=ns
    return out,tape,p,q
def render(tape,p,q):
    if not tape: return ""
    lo=min(min(tape),p);hi=max(max(tape),p)
    s="".join(("1" if tape.get(i,0) else "0") for i in range(lo,hi+1))
    return s[:p-lo]+"["+"ABCDEFGH"[q]+"]"+s[p-lo:]
if __name__=="__main__":
    N=int(sys.argv[1])
    o,tape,p,q=run(N)
    print(render(tape,p,q))
