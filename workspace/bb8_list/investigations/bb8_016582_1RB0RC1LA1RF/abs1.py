import sys
def step(j,a,ds):
    """abstract macro step; returns new (j,a,ds) or None if no rule"""
    ds=tuple(ds)
    if j%3==2:
        if a>=2: return (j+3,a-1,ds)   # (batch this in caller)
        # a==1
        if not ds: return (2,2*j+37,())
        d=ds[0]; S=ds[1:]
        if d>=5: return (j+20,d-4,S)
        if d==4:
            if not S: return (1,2*j+49,())
            if S[0]>=4: return (1,2*j+49,(S[0]-4,)+S[1:])
            return None
        return None
    if j%3==1:
        if a>=5:
            if j==1:
                if a>=13: return (2,14,(a-12,)+ds)
                return None
            return (2,2*j-3,(a-4,)+ds)
        if a==1:
            if not ds: return (2,2*j+21,())
            return (j+12,ds[0],ds[1:])
        return None
    return None
def run(j,a,ds,maxr=60,verbose=True):
    n=0
    while n<maxr:
        # batch normal steps
        if j%3==2 and a>=2:
            j,a=j+3*(a-1),1
        r=step(j,a,ds)
        if verbose:
            def s(x): return str(x) if x<10**12 else "~10^%d"%(len(str(x))-1)
            print(n,"R(",s(j),",",s(a),"|",[s(x) for x in ds][:8],len(ds),")")
        if r is None: print("STUCK",j%3,a if a<50 else "big",[x if x<50 else "big" for x in ds][:4]);return
        j,a,ds=r;n+=1
if __name__=="__main__":
    run(2,14,(44,))
