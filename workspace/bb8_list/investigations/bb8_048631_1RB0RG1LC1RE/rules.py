import sys
def strip(ds):
    ds=list(ds)
    while ds and ds[0]==0: ds.pop(0)
    return tuple(ds)
def tz(ds):
    k=0
    while k<len(ds) and ds[len(ds)-1-k]==0: k+=1
    return k
def step(ds,a,b):
    """rule-level successor; returns (kind,(ds,a,b)) or (kind,None) if rule unavailable"""
    ds=list(ds)
    if a>=1: return 'R1',(tuple(ds),a-1,b+1)
    k=tz(ds)
    if k==len(ds):
        if b<1: return 'R4?',None
        return 'R4',((1,)*b,1,0)
    if k==0:
        if b<1: return 'R2?',None
        ds[-1]-=1
        return 'R2',(strip(ds),b+1,0)
    i=len(ds)-1-k
    if k<b:
        ds[i]-=1
        ds=ds[:i+1]+[b+1-k]+[1]*(k-1)
        return 'R3',(strip(ds),1,0)
    return 'R3big',None
if __name__=='__main__':
    ds,a,b=(),1,0
    N=int(sys.argv[1]); n=0
    mn=10**9; 
    while n<N:
        kd,r=step(ds,a,b)
        if r is None: print('stuck',kd,ds,a,b); break
        if kd=='R3':
            k=tz(ds); mn=min(mn,b-k)
        ds,a,b=r; n+=1
    print(n,len(ds),max(ds) if ds else 0,b,'min b-k',mn)
