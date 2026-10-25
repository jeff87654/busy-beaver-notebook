from lit import parse,TM
import sys
T=parse(TM)
def run(cells,pos,q,N,show=True):
    tape={i:c for i,c in enumerate(cells) if c}
    p=pos
    for n in range(N):
        s="".join(str(tape.get(i,0)) for i in range(min(-3,min(tape)-2),max(tape)+4)) 
        lo=min(-3,min(tape)-2)
        if show: print(n,"ABCDEFGH"[q], s[:p-lo]+"["+s[p-lo]+"]"+s[p-lo+1:])
        r=T[(q,tape.get(p,0))]
        if r is None: print("HALT");return
        w,d,ns=r
        if w: tape[p]=1
        else: tape.pop(p,None)
        p+=d;q=ns
cells=[1,1,1,1]+[0]*8+[1,0,0,0,0,1,0,1]
run(cells,4,0,int(sys.argv[1]))
