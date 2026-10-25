import sys, itertools
sys.path.insert(0,'.')
from kfam import *
set_shape('D','1')
M='1LB1LA_0RC0RF_0LD1RC_1LA1LG_1LZ0LA_1RB1RF_1RH1LE_0RI1RH_1RB0RH'
def tz(ds):
    k=0
    while k<len(ds) and ds[len(ds)-1-k]==0: k+=1
    return k
def pred(ds,a,b):
    ds=list(ds)
    if a>=1:
        if not ds and a==1: return pred_r4(b+3)
        return ('K',(tuple(ds),a-1,b+3))
    k=tz(ds)
    if k==len(ds): return pred_r4(b)
    i=len(ds)-1-k
    if k==0:
        ds[-1]-=1
        return ('K',(strip(ds),b+2,1))
    if 2*k<=b:
        ds[i]-=1
        ds=ds[:i+1]+[b+2-2*k]+[2]*(k-1)
        return ('K',(strip(ds),2,1))
    if 2*k==b+1: return ('HALT',)
    return None
def pred_r4(b):
    if b%2==1: return ('HALT',)
    return ('K',((2,0)+(1,0)*(b//2),1,0))
def cases():
    for n in range(0,5):
        for ds in itertools.product(range(0,4),repeat=n):
            if ds and ds[0]==0: continue
            for a in range(0,3):
                for b in range(1,10):   # b>=1 ; also b=0 separately
                    yield ds,a,b
if __name__=='__main__':
    bad=0; tot=0; unp=0
    for ds,a,b in cases():
        p=pred(ds,a,b)
        r=run_next(M,ds,a,b,N=10**5)
        tot+=1
        if p is None:
            unp+=1; continue
        if p[0]=='HALT':
            ok = r[0]=='HALT'
        else:
            ok = r[0]=='K' and r[2]==p[1]
        if not ok:
            bad+=1
            if bad<40: print('MISMATCH',ds,a,b,p,r[:3])
    print('tot',tot,'unpredicted',unp,'bad',bad)
