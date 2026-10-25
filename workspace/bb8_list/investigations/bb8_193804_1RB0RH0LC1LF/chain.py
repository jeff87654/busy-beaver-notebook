from fam import *
from pipe import *
import sys
def chain(k, verbose=False):
    """10 rounds starting at B0 with k near copies; returns list of (name, start, target, script)"""
    out=[]; ph,c,K=('B',0,k)
    for i in range(10):
        delta=-2 if ph=='B' else 3
        t=c+delta; dT=t//5; c2=t%5
        K2=K+dT
        nph='A' if ph=='B' else 'B'
        cfg=family(ph,K,0,c); tgt=family(nph,K2,0,c2)
        name='%s%d'%(ph,c)
        script,end=drive(name,cfg,tgt,matchers=[pipe_matcher()],maxev=400,verbose=False)
        ok=script[-1][0]=='end'
        out.append((name,(ph,K,c),(nph,K2,c2),script if ok else None))
        if not ok: print('FAIL',name,K,script[-2:]); break
        ph,c,K=nph,c2,K2
    return out
if __name__=='__main__':
    k=int(sys.argv[1])
    for nm,s,t,sc in chain(k): print(nm,s,'->',t,'ops',len(sc) if sc else None)
