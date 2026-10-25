import sys
M="1RB0LC_0RC0RF_0RD0RH_1LE---_0LF1LG_1RD1LA_1RC1LA_0LF0LA"
T={}
for i,ch in enumerate(M.split("_")):
    for s in (0,1):
        e=ch[3*s:3*s+3]
        T[(i,s)]=None if e=="---" else (int(e[0]),1 if e[1]=="R" else -1,ord(e[2])-65)
def run(n,show=()):
    tape={};p=0;q=0;out=[]
    for t in range(n):
        if t in show: out.append((t,q,p,dict(tape)))
        r=T[(q,tape.get(p,0))]
        if r is None: return t,q,p,tape,out
        w,d,ns=r; tape[p]=w; p+=d; q=ns
    return n,q,p,tape,out
def render(tape,p,q):
    ks=[k for k,v in tape.items() if v]+[p]
    lo,hi=min(ks),max(ks)
    s=""
    for k in range(lo,hi+1):
        c=str(tape.get(k,0))
        s+= ("["+"ABCDEFGH"[q]+"]"+c) if k==p else c
    return s
if __name__=="__main__":
    n=int(sys.argv[1])
    t,q,p,tape,_=run(n)
    print(t,"ABCDEFGH"[q],p); print(render(tape,p,q))
