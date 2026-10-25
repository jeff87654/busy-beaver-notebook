"""K-level model of M1/M2 (p101 family).  State (mode, ds, a, b):
 mode 'H': tape = P101 + K-list [0]+ds ; mode 'D': tape = plain list ds (no P; leading zero digits invisible);
 mode 'O': odd intermediate [1,3,2b+3] (only after E(1,b)); mode 'S': single block [Y] (ds=[], a=0, value in b as Y).
Returns next state or ('HALT',why) / ('OUT',why) if outside the fitted domain."""
from blk import word_of, blocks
def enc(st):
    m,ds,a,b=st
    if m=='S': return [b]
    if m=='O': return [1,3,2*b+5]
    if m=='H': w='10100'
    else: w=''
    for d in ds: w+='10'*d+'00'
    w+='10'*a+'00'+'10'*(2*b+1)+'1'
    return blocks(w)
def step(st):
    m,ds,a,b=st
    ds=list(ds)
    if m=='S':
        Y=b
        if Y<4: return ('OUT','small single %d'%Y)
        c=Y//2
        return ('H',[2]*(c-2),2,Y%2)
    if m=='O':
        return ('S',[],0,2*b+7)
    if a>=1: return (m,ds,a-1,b+1)
    nz=[i for i,d in enumerate(ds) if d]
    if nz:
        if ds[-1]>=1:
            if b<1: return ('OUT','R2 b=0')
            ds[-1]-=1; return (m,ds,2*b+2,0)
        k=len(ds)-1-nz[-1]
        if b<k+1: return ('OUT','R3 b=%d<k+1, k=%d'%(b,k))
        ds[nz[-1]]-=1
        ds[nz[-1]+1:]=[2*b+2-2*k]+[2]*(k-1)
        return (m,ds,2,0)
    # all zero, a=0
    if m=='D': return step(('S',[],0,2*b+2))
    n=len(ds)+1
    if n==1:
        if b<1: return ('OUT','E(1,0) halts')
        return ('O',[],0,b)
    if b<n: return ('OUT','E(%d,%d) b<n'%(n,b))
    X=2*b+5-2*n
    if n==2: return ('D',[1],X,1)
    return ('D',[1,X]+[2]*(n-3),2,1)
