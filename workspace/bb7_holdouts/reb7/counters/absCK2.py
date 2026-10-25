import idle, random, sys
from thr import rlg
from trace_check import expand
import sys as _s
M,OO,QQ,UU,SS_,SL,PRE=_s.argv[1:8]
PRE_RLE='.'.join(PRE)+'.' if len(set(PRE))==1 and len(PRE)==1 else PRE
# CHECK row map: digits ds (u=11 runs), a=0, y odd (template b=2b+1), prefix '1', S=1011
def astep(ds,y):
    ds=list(ds)
    if ds[-1]>=1: ds[-1]-=1; return tuple(ds),2*y+3
    i=len(ds)-1
    while i>=0 and ds[i]==0: i-=1
    K=len(ds)-1-i
    if i>=0:
        v=y+1-K
        if v<1: return None
        ds[i]-=1; return tuple(ds[:i+1]+[v]+[1]*(K-1)),3
    if K==1: return (tuple([1]*(y-1)+[0]),11) if y>=2 else None
    if K==2: return tuple([1]*y),5
    j=y+2-K
    if j<1: return None
    return tuple([1]*j+[2]+[1]*(K-3)),3
def lit_next(ds,y,N=10**8):
    for l in rlg(M,OO,QQ,UU,SS_,SL,'P:'+PRE+' '+' '.join(map(str,list(ds)+[0,y])),N,40,0):
        if l.startswith('H'): return 'H'
        if l.count('|')<2: return l
        _,P,r=l.split('|',2)
        if P.strip()!=PRE_RLE: continue
        r=expand(r.split())
        if r[-2]==0 and r[-1]%2==1 and r[-1]>=3: return (tuple(r[:-2]),r[-1])
    return None
if __name__=='__main__':
    random.seed(5); ok=bad=0
    for it in range(int(sys.argv[8])):
        L=random.randint(1,5); ds=tuple(random.choice([0,0,0,1,2,3]) for _ in range(L))
        y=2*random.randint(L+2,L+12)+1
        a=astep(ds,y)
        if a is None: continue
        g=lit_next(ds,y)
        if g==a: ok+=1
        else: bad+=1; print('MISMATCH',ds,y,'exp',str(a)[:60],'lit',str(g)[:60])
    print('ok',ok,'bad',bad)
