import idle, random
from sim import parse, X
T=parse(X)
def runN(cells, pos, st, N):
    tape=dict(enumerate(cells))
    for n in range(N):
        s=tape.get(pos,0); tr=T[(st,s)]
        if tr is None: return None
        w,d,ns=tr; tape[pos]=w; pos+=d; st=ns
    lo=min(tape); hi=max(tape)
    return [tape.get(i,0) for i in range(lo,hi+1)], pos-lo, st
random.seed(5); bad=0
for _ in range(300):
    left=[random.randint(0,1) for _ in range(random.randint(0,8))]+[1]   # cell left of zero block (any), here ends with 1 (y+1 digit)
    m=random.randint(2,6); c=random.randint(2,40); t=random.randint(0,6); right=[random.randint(0,1) for _ in range(5)]
    def Q(m,c,t): 
        cells=[0]*5+left+[0]*m+[1]*c+[0,1,1]*t+[0]+right
        return cells, 5+len(left)+m-1
    cells,pos=Q(m,c,t)
    r=runN(cells,pos,4,2*c+5)
    exp,epos=Q(m-1,c-2,t+1)
    # compare: trim
    if r is None or r[2]!=4: bad+=1; print('bad state',m,c,t); continue
    got,gpos,_=r
    # align by position of head: exp head epos
    off=gpos-epos
    g=got[off:off+len(exp)] if off>=0 else None
    if g!=exp or any(got[:off]) or any(got[off+len(exp):]): bad+=1; print('MISS',m,c,t)
print('loop lemma Q(m,c,t)->Q(m-1,c-2,t+1) in 2c+5 steps: bad',bad,'of 300')
