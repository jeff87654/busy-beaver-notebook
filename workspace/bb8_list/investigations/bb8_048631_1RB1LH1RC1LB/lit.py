from sim import parse,M
T=parse(M)
def lit(state,left,right,maxsteps=10**6,stop=None):
    """left: list nearest-head-first, right: list starting at head cell; blank beyond. returns (state,left,right) when stop(state,tape..) or halted"""
    L=list(left);R=list(right)
    s='ABCDEFGH'.index(state);n=0
    while n<maxsteps:
        if stop and stop(s,L,R,n): return 'ABCDEFGH'[s],L,R,n
        c=R.pop(0) if R else 0
        tr=T[(s,c)]
        if tr is None: return 'HALT',L,R,n
        w,d,q=tr
        if d=='R': L.insert(0,w)
        else:
            R.insert(0,w); x=L.pop(0) if L else 0; R.insert(0,x)
        s=q;n+=1
    return None
def norm(L):
    L=list(L)
    while L and L[-1]==0: L.pop()
    return L
def S(x): return [int(c) for c in x]
