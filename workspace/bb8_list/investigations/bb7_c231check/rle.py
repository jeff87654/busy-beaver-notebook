import sys; from sim import *
from itertools import groupby
def rle(tape,h,s,lo,hi):
    # render with head marker, RLE
    cells=[(tape.get(i,0), i==h) for i in range(lo,hi+1)]
    out=[]; 
    for (v,hd),g in groupby(cells):
        n=len(list(g))
        if hd: out.append(f"<{'ABCDEFG'[s]}>{v}")
        else: out.append(f"{v}^{n}" if n>1 else str(v))
    return ' '.join(out)
def run(M,A,B,ev):
    T=parse(M); tape={}; h=0; s=0; step=0
    while step<B:
        b=tape.get(h,0); t=T[(s,b)]
        if t is None: print('HALT',step, rle(tape,h,s,min(tape)-1,max(tape)+1)); return
        if step>=A and ev(s,b):
            ks=[k for k,v in tape.items() if v]
            print(step, rle(tape,h,s,min(ks+[h])-1,max(ks+[h])+1))
        tape[h]=t[0]; h+=t[1]; s=t[2]; step+=1
if __name__=='__main__':
    A,B=int(sys.argv[1]),int(sys.argv[2]); evs=sys.argv[3]
    import os; MM=M2 if os.environ.get("MM")=="2" else M1
    run(MM,A,B,lambda s,b: ('ABCDEFG'[s]+str(b)) in evs.split(','))
