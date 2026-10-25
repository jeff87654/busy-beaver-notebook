import idle, sys, random
from rsim import *
def isk(r): return r.s==4 and r.h==0 and not r.L
def nextk(M,a,ds,maxs=10**6):
    r=kconfig(M,a,ds)
    while True:
        res=r.run_until(isk,maxs)
        if res=='HALT': return ('HALT',r.steps,r.ones(),r)
        if res=='TIMEOUT': return ('TO',r.steps)
        k=parse_k(r)
        if k: return ('K',r.steps,k)
def pred(a,ds):
    # ds: active end first
    if ds and ds[0]>0: return ('K',(3*a+3,[ds[0]-1]+ds[1:]))
    k=0
    while k<len(ds) and ds[k]==0: k+=1
    if k==len(ds): return ('HALT',)
    return ('K',(1,[3*a+3-k]+[1]*(k-1)+[ds[k]-1]+ds[k+1:]))
if __name__=='__main__':
    M = M1 if sys.argv[1]=='1' else M2
    bad=0; n=0
    for a in range(0,12):
        for ds in ([1],[2],[3,1],[1,0,2],[0],[0,0],[0,0,0],[0,1],[0,0,1],[0,0,0,2],[0,0,0,0,1],[0]*6+[3],[0,5,0]):
            p=pred(a,ds); r=nextk(M,a,ds)
            ok = (p[0]=='HALT' and r[0]=='HALT') or (p[0]=='K' and r[0]=='K' and tuple(r[2])==(p[1][0],p[1][1]))
            n+=1
            if not ok:
                bad+=1; print('MISMATCH a=',a,'ds=',ds,'pred',p,'got',r[:3])
    print('done',n,'bad',bad)
