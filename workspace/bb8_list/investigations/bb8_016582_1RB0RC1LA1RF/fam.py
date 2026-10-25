from lit import parse, TM
T=parse(TM)
def build(j,a,ds,pre=None):
    """R(j,a|ds) : A> 0 11 (01)^j 0^a 1 0^4 1 0 1 [0^d 1 0^4 1 0 1]* ; head at leftmost 0 state A. returns (tape dict, p, q)"""
    cells=[0,1,1]
    for _ in range(j): cells+= [0,1]
    cells+=[0]*a+[1,0,0,0,0,1,0,1]
    for d in ds: cells+=[0]*d+[1,0,0,0,0,1,0,1]
    tape={i:1 for i,c in enumerate(cells) if c}
    return tape,0,0
def gaps(tape):
    ones=sorted(tape)
    return [ones[i+1]-ones[i]-1 for i in range(len(ones)-1)]
def parseR(tape):
    g=gaps(tape)
    if not g or g[0]!=0: return None
    i=1
    while i<len(g) and g[i]==1: i+=1
    j=i-1
    # after 1^j comes a (>=2 or absorb) then 4,1 then digits (d,4,1)*
    rest=g[i:]
    # option a=1 absorb: if rest starts with 4,1 : a=1,j-=1
    if rest[:2]==[4,1] and j>=1: j-=1; a=1; rest=rest[0:]
    else:
        if not rest or rest[0]<2: return None
        a=rest[0]; rest=rest[1:]
    if rest[:2]!=[4,1]: return None
    rest=rest[2:]
    ds=[]
    while rest:
        if len(rest)<3 or rest[1:3]!=[4,1]: return None
        ds.append(rest[0]); rest=rest[3:]
    return (j,a,tuple(ds))
def step_R(j,a,ds,maxsteps=300000):
    tape,p,q=build(j,a,ds)
    n=0; lo=min(tape)-1
    first=True
    while n<maxsteps:
        r=T[(q,tape.get(p,0))]
        if r is None: return ('HALT',n,sum(tape.values()))
        w,d,ns=r
        if w: tape[p]=1
        else: tape.pop(p,None)
        p+=d;q=ns;n+=1
        if q==0 and p<lo:
            lo=p
            R=parseR(tape)
            if R: return (R,n)
        if p<lo: lo=p
    return None
if __name__=="__main__":
    import sys
    for j in (2,3,5):
        for a in (1,2,3,4):
            for ds in ((),(12,),(20,)):
                print(j,a,ds,step_R(j,a,ds))
