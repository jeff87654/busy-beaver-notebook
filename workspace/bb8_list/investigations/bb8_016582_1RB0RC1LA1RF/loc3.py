from lit import parse,TM
import sys
T=parse(TM)
def run(cells,pos,q,N):
    tape={i:c for i,c in enumerate(cells) if c}
    p=pos
    out=[]
    for n in range(N):
        if q==0 and p<min(tape):
            ones=sorted(tape); g=[ones[i+1]-ones[i]-1 for i in range(len(ones)-1)]
            out.append((n,g[:8]))
            if len(out)>=2: break
        r=T[(q,tape.get(p,0))]
        if r is None: out.append("HALT");break
        w,d,ns=r
        if w: tape[p]=1
        else: tape.pop(p,None)
        p+=d;q=ns
    return out
for left in ([1,1],[1,1,1],[1,1,1,1],[1],[1,1,1,1,1],[1,0,1,1],[1,1,1,0,1,1]):
    cells=left+[0]*10+[1,0,0,0,0,1,0,1]
    print(left,run(cells,len(left),0,3000))
