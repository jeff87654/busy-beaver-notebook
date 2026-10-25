import sys
sys.setrecursionlimit(10000)
# abstract machine: state (ds farthest-first list, a, b); rules R1-R3, halt at R4
def step(ds,a,b):
    if a>0: return (ds,a-1,2*b+2)
    k=0
    while k<len(ds) and ds[len(ds)-1-k]==0: k+=1
    if k==len(ds): return None  # halts
    i=len(ds)-1-k
    x=ds[i]
    if k==0:
        nd=list(ds); nd[i]=x-1
        return (nd,2*b+2,0)
    nd=list(ds[:i])+[x-1,2*b+2]+[0]*(k-1)
    return (nd,0,0)
def run_to_zero(ds,b,maxsteps=10**7):
    st=(list(ds),0,b); n=0
    while n<maxsteps:
        if all(d==0 for d in st[0]) and st[1]==0: return st[2],n
        r=step(*st)
        if r is None: return st[2],n
        st=r;n+=1
    return None
def A(n,D):
    return run_to_zero([D]+[0]*n,0)
if __name__=='__main__':
    for n in range(0,3):
        for D in range(0,4):
            r=A(n,D)
            if r: 
                b,steps=r
                print(n,D,len(str(b)) if b>10**6 else b,steps)
