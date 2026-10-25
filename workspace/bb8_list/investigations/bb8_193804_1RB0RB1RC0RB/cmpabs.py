import re, sys
from sim import T
def step(l, ds):
    d=list(ds)+[0,0,0,0]
    if not l.startswith('0000'): l='0000'+l
    if d[0]==3 and d[1]>=1: return 'R1', l+'0', [3,d[1]-1]+d[2:]
    if d[0]==3 and d[1]==0: return 'R2', l+'01', [0,1]+d[2:]
    if d[0]==0 and d[1]==3 and d[2]>=1: return 'R4', l+'01', [3,d[2]-1]+d[3:]
    if d[0]==0 and d[1]==1:
        m=re.search(r'0001((01)*)$',l)
        if not m: return 'STUCK-L', l, ds
        k=len(m.group(1))//2
        if k%2: return 'STUCK-ODD', l, ds
        mm=k//2; lp=l[:m.start()]
        if d[2]>=1: return 'R3', lp, [3]*(mm+2)+[d[2]-1]+d[3:]
        else: return 'R5', lp+'1', [0]+[3]*(mm+1)+[1]+d[3:]
    return 'STUCK', l, ds
def norm(l,ds):
    l=l.lstrip('0'); ds=list(ds)
    while ds and ds[-1]==0: ds.pop()
    return l,tuple(ds)
def tm_h_events(nsteps, start):
    tape={};pos=0;st='A'
    for i in range(nsteps):
        if st=='H' and i>=start:
            lo=min(tape);hi=max(tape)
            L=''.join(str(tape.get(p,0)) for p in range(lo,pos))
            R=''.join(str(tape.get(p,0)) for p in range(pos,hi+1)).rstrip('0')
            yield i,L,R
        s=tape.get(pos,0);tr=T[(st,s)]
        if tr is None: print('HALT',i); return
        tape[pos]=tr[0];pos+=tr[1];st=tr[2]
def parse(R):
    assert R=='' or R[0]=='0', R
    return [len(x) for x in R.split('0')[1:]] if R else []
if __name__=="__main__":
    N=int(sys.argv[1]); S=int(sys.argv[2])
    cur=None; cnt={}
    for i,L,R in tm_h_events(N,S):
        if R and R[0]!='0': print('head on 1 at',i); break
        st=norm(L,parse(R+'0'))
        if cur is not None and st!=cur: print('MISMATCH at',i,cur,st); break
        r,l2,d2=step(*st); cnt[r]=cnt.get(r,0)+1
        if r.startswith('STUCK'): print(r,i,st); break
        cur=norm(l2,d2)
    print(cnt)
