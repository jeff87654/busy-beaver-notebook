"""Semi-abstract K-form simulator.  State: tokens = list of (val, huge) ; r = int or 'H' (huge, = 2 mod 3).
huge token: val is a representative >= 6 of the true residue class mod 3.  Oracle = literal machine on small representatives."""
import sys
from batch import run
def show(toks,r):
    return '['+','.join(('%d~'%v if h else str(v)) for v,h in toks)+'] r=%s'%r
def oracle(vals,N=2000000000):
    cf=[(vals,r) for r in (2,5,8)]
    res=run(cf,tail='111001',N=N)
    outs=[x for _,_,x in res]
    if not all(isinstance(x,tuple) for x in outs): return ('FAIL',[x if not isinstance(x,tuple) else 'ok' for x in outs])
    L=len(outs[0][1])
    if any(len(x[1])!=L for x in outs): return ('FAIL','length depends on r')
    toks=[];
    for i in range(L):
        v2,v5,v8=[x[1][i] for x in outs]
        if v5-v2!=v8-v5: return ('FAIL','nonaffine token')
        beta=(v5-v2)//3
        if beta*3!=v5-v2: return ('FAIL','nonint slope')
        if beta==0: toks.append((v2,False))
        else: toks.append((v8,True))   # huge; class of v8 = class of alpha+2beta
    r2,r5,r8=[x[2] for x in outs]
    if r5-r2!=r8-r5: return ('FAIL','nonaffine r')
    rr=('H' if r5!=r2 else r2)
    return ('OK',toks,rr,outs[0][0])
def step(toks,r,N=2000000000,verbose=True):
    toks=list(toks)
    a,ah=toks[-1]
    if ah or a>=3:
        cls=a%3
        j=(a-cls)//3
        if ah or r=='H':
            toks[-1]=(cls,False); r='H'
        else:
            for _ in range(j): r=2*r+4
            toks[-1]=(cls,False)
            if r>10**9: r='H'
        return 'R1chain',toks,r
    # a in 0,1,2 : oracle on representatives
    vals=[v for v,h in toks]
    if r!='H':
        res=run([(vals,r)],tail='111001',N=N)
        x=res[0][2]
        if not isinstance(x,tuple): return 'FAIL',x,None
        return 'F',[(v,False) for v in x[1]],x[2]
    o=oracle(vals,N)
    if o[0]!='OK': return 'FAIL',o,None
    return 'F',o[1],o[2]
if __name__=='__main__':
    toks=eval(sys.argv[1]); r=eval(sys.argv[2]); maxst=int(sys.argv[3])
    st=[(v,h) for v,h in toks]
    print(show(st,r))
    for i in range(maxst):
        kind,t,rr=step(st,r)
        if kind=='FAIL': print('FAIL',t,rr); break
        if kind=='R1chain':
            st,r=t,rr; continue
        st,r=t,rr
        print(kind,show(st,r),flush=True)
