from lit import parse,TM
import sys
T=parse(TM)
def run(cells,pos,q,N):
    tape={i:c for i,c in enumerate(cells) if c}
    p=pos
    for n in range(N):
        if q==0 and p<min(tape):
            ones=sorted(tape); g=[ones[i+1]-ones[i]-1 for i in range(len(ones)-1)]
            print(n,g)
        r=T[(q,tape.get(p,0))]
        if r is None: print("HALT");return
        w,d,ns=r
        if w: tape[p]=1
        else: tape.pop(p,None)
        p+=d;q=ns
for n0 in (6,12,18):
    print("n0",n0)
    cells=[1,1,1,1]+[0]*n0+[1,0,0,0,0,1,0,1]
    run(cells,4,0,20000)
