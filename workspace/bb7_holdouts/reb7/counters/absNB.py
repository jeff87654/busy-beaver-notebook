import idle, random, sys
import nb
# NOBOUNDARY abstract map at a=0 moments: state (ds tuple of values, y even raw); b=y/2
def astep(ds,y):
    ds=list(ds); b=y//2
    if ds and ds[-1]>=1:
        ds[-1]-=1; return tuple(ds), 2**(b+3)-4
    i=len(ds)-1
    while i>=0 and ds[i]==0: i-=1
    if i>=0:
        ds[i]-=1; ds[i+1]=b; return tuple(ds),4
    if b<1: return None
    return tuple([b-1]+([1]+ds[1:] if ds else [])),4
if __name__=='__main__':
    M,O,Q=sys.argv[1:4]; n=int(sys.argv[4])
    if len(sys.argv)>5: nb.SS=sys.argv[5]
    random.seed(3); ok=bad=0
    for it in range(n):
        L=random.randint(1,4)
        ds=tuple(random.choice([0,0,1,2,3,4]) for _ in range(L))
        y=2*random.randint(1,9)
        if ds[-1]>=1 and y>14: y=random.choice([2,4,6,8])
        a=astep(ds,y)
        got=nb.moments(M,O,Q,list(ds),0,y,2)
        g=[x for x in got if isinstance(x,tuple)]
        # first template moment may be the start itself
        g=[x for x in g if x!=(ds,y)]
        if g and g[0]==a: ok+=1
        else: bad+=1; print('MISMATCH',ds,y,'exp',a,'lit',got)
    print('ok',ok,'bad',bad)
