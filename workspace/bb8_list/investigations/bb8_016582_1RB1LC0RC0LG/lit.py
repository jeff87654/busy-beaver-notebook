import sys
TM="1RB1LC_0RC0LG_1RD0RD_1LE1LD_1RH0LF_1LG0RA_---1RA_1RD1RH"
def parse(tm):
    t={}
    for i,c in enumerate(tm.split("_")):
        for s in (0,1):
            e=c[3*s:3*s+3]
            t[(i,s)]=None if e=="---" else (int(e[0]),1 if e[1]=="R" else -1,ord(e[2])-65)
    return t
T=parse(TM)
def edges(N,maxev=60):
    tape={};p=0;q=0;lo=0;ev=[]
    for n in range(N):
        if p<lo:
            lo=p
            ev.append((n,q,p,dict(tape)))
        r=T[(q,tape.get(p,0))]
        if r is None: print("undef",n,"ABCDEFGH"[q],tape.get(p,0));return ev,tape
        w,d,ns=r
        if w: tape[p]=1
        else: tape.pop(p,None)
        p+=d;q=ns
    return ev,tape
def rend(tape,p,q,lo=None):
    if lo is None: lo=min(tape)
    hi=max(max(tape),p)
    return "".join(("1" if tape.get(i,0) else "0") for i in range(min(lo,p),hi+1)).__str__()
if __name__=="__main__":
    ev,tape=edges(int(sys.argv[1]))
    for n,q,p,t in ev[:int(sys.argv[2])]:
        hi=max(t) if t else p
        print(n,"ABCDEFGH"[q],"".join(str(t.get(i,0)) for i in range(p,hi+1)))
