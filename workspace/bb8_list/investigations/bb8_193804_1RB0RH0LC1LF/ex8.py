from fam import *
from pipe import *
import sys
K1,K2=int(sys.argv[1]),int(sys.argv[2])
for ph in 'BA':
    for c in range(5):
        delta=-2 if ph=='B' else 3
        t=c+delta; dT=t//5; c2=t%5
        k1t,k2t=K1,K2
        if dT<0: (k2t:=k2t+dT) if K2+dT>=0 else (k1t:=k1t+dT)
        if dT>0: k1t+=dT
        cfg=family(ph,K1,K2,c)
        tgt=family('A' if ph=='B' else 'B',k1t,k2t,c2)
        try:
            script,end=drive('%s%d'%(ph,c),cfg,tgt,matchers=[pipe_matcher()],maxev=400,verbose=False)
            ok=script[-1][0]=='end'
            lit=sum(o[1] for o in script if o[0] in('steps','end'))
            print(ph,c,'->',tgt[0],c2,'OK' if ok else 'FAIL '+str(script[-2:]),'ops',len(script),'lit steps',lit)
        except Exception as e:
            print(ph,c,'EXC',repr(e)[:200])
