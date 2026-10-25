"""ph.py M WORD STEPS MAXEV: like fol.py but suppresses R1 steps (a-1,b+1) and R2 (last digit -1, a=2b+2,b=0) steps."""
import idle, sys
from fol import follow, rle
M=sys.argv[1]
out=follow(M,sys.argv[2],int(sys.argv[3]),int(sys.argv[4]),quiet=True)
prev=None
for e in out:
    if e[0] in ('H','T'): print(e); break
    st,gap,g=e
    if g and len(g)==4:
        P,ds,a,b=g
        skip=False
        if prev and len(prev)==4 and prev[0]==P:
            if prev[1]==ds and a==prev[2]-1 and b==prev[3]+1: skip=True
            if len(ds)==len(prev[1]) and ds[:-1]==prev[1][:-1] and ds and ds[-1]==prev[1][-1]-1 and prev[2]==0 and a==2*prev[3]+2 and b==0: skip=True
        if not skip: print(st,'P=%s'%P[:40],rle(ds),a,b, '' if not prev or len(prev)!=4 else '<- from %s %s %d %d'%(prev[0][:20],rle(prev[1]),prev[2],prev[3]))
        prev=g
    else:
        print(st,'raw',g[1][:120] if g else None); prev=g
