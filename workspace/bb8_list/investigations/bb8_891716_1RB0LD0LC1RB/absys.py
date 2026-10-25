"""Abstract model F(W,b): W nearest-first digits (W[0] = a), b' = 2b+1."""
import sys,os,random
sys.path.insert(0,'C:/Users/jeffr/Downloads/bb8/bb8_list/investigations/neighbors_family_tools')
os.environ['BB_KENC']='10,0'
def norm(W):
    W=list(W)
    while W and W[-1]==0: W.pop()
    return tuple(W)
def step(W,b):
    W=list(W)
    if W and W[0]>0:
        W[0]-=1; return norm(W),b+1,'R1'
    j=0
    while j<len(W) and W[j]==0: j+=1
    if j==len(W):
        return tuple([2]*b),1,'R4'
    y1=W[j]; t=W[j+1:]
    if j==0: raise Exception
    if j<=b:
        return norm([2]*(j-1)+[2*b-2*j+2,y1-1]+t),1,'R3A' if j>1 else 'R2'
    if j==b+1:
        return norm([2]*(b-1)+[y1+2]+t),1,'R3B'
    return norm([2]*b+[0]*(j-b-2)+[y1]+t),1,'R3C'
def to_kfam(W,b):
    W=list(W)
    a=W[0] if W else 0
    ds=tuple(reversed(W[1:]))
    return ds,a,2*b+1
if __name__=='__main__':
    from kfam import run_next, set_shape
    TM=os.environ.get('TM',"1RB0LD_0LC1RB_1LB1LA_1RE0LH_0RF1LE_0RA0RG_0RC0LE_1LD---")
    set_shape('B','011')
    rnd=random.Random(int(sys.argv[1]) if len(sys.argv)>1 else 1)
    bad=0;n=0;kinds={}
    for it in range(int(sys.argv[2]) if len(sys.argv)>2 else 300):
        b=rnd.randint(1,9)
        L=rnd.randint(0,8)
        W=[rnd.choice([0,0,0,1,2,3,4]) for _ in range(L)]
        # force a zero-run at the front sometimes
        if rnd.random()<0.7:
            j=rnd.randint(0,b+4); W=[0]*j+[rnd.randint(1,4)]+W
        W=list(norm(W))
        if W and W[0]>6: continue
        W2,b2,kind=step(W,b)
        if not W2: W2,b2,_k=step(W2,b2)
        ds,a,bp=to_kfam(W,b)
        v=run_next(TM,ds,a,bp,N=5*10**6)
        n+=1; kinds[kind]=kinds.get(kind,0)+1
        if v[0]!='K': print('NOK',W,b,v[:2]); bad+=1; continue
        ds2,a2,bp2=v[2]
        W2l=norm([a2]+list(reversed(ds2)))
        # kfam may hit K at a point... compare
        if (W2l,bp2)!=(W2,2*b2+1):
            print('MISMATCH',W,b,'abstract',W2,2*b2+1,kind,'literal',W2l,bp2); bad+=1
    print('checked',n,'bad',bad,kinds)
