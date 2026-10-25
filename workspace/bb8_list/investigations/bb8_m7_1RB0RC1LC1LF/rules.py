import sys
sys.path.insert(0,'../rebuilder_nbrs')
from usage_phases import Tmpl, parse_tm, ST, run
from r4grid import mirror, tmpl_from
M='1RB0RC_1LC1LF_1RD0LB_1RA1LE_1LG0LC_0LG1LE_0RH1RC_0RA---'
TS='L,G,P=1001,u=010,s=001,d=1d+0,b=1b+0,S=-'
o,T=tmpl_from(TS)
tm=parse_tm(mirror(M))
def lit(ds,a,b,cap=3000000):
    return run(tm,T,T.build(tuple(ds),a,b),stop_any=True,cap=cap)
def R(ds,a,b):
    ds=list(ds)
    if a>=1: return (tuple(ds),a-1,b+1)
    # a==0
    if not ds or all(x==0 for x in ds):
        return None
    if ds[-1]>=1:
        ds[-1]-=1; return (tuple(ds),b,1)
    # trailing zeros
    k=0
    while ds[-1-k]==0: k+=1
    idx=len(ds)-1-k
    # digit ds[idx]>=1; ds = pre + [y+1] + 0^k
    ds2=ds[:idx]+[ds[idx]-1]+[b]+[0]*(k-1)
    return (tuple(ds2),0,1)
if __name__=='__main__':
    import itertools
    bad=0;tot=0
    for k in range(0,9):
        for b in range(1,10):
            for a in range(0,3):
                for pre in [(1,),(2,),(1,0),(3,2)]:
                    ds=pre+(0,)*k
                    out,st,use,kf=lit(ds,a,b)
                    exp=R(ds,a,b)
                    tot+=1
                    got=kf if out=='FAMILY' else out
                    if exp is None: continue
                    if got!=exp:
                        bad+=1
                        if bad<40: print('MISMATCH',ds,a,b,'got',got,'exp',exp)
    print(tot,bad)
