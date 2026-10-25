import sys, os, time
sys.path.insert(0,'C:/Users/jeffr/Downloads/bb8/bb8_list/investigations/bb8_891716_1RB0LD0LC1RB')
from rules891 import *
import engine
pl.set_tm(TM)
nm=sys.argv[1]
s,t=rules()[nm]
cfg=s
ops,cfg,how=engine.run_until_stuck(cfg,None,target=t)
lp=engine.accelerate(cfg,1)
print('loop on',lp['v'],lp['v2'])
print('resultB',pl.show(lp['resultB']))
tgt=engine.subst(t,lp['v'],((lp['v2'],1),),1)
cfg=lp['resultB']
for i in range(6):
    ops,cfg,how=engine.run_until_stuck(cfg,None,target=tgt)
    print('stage',i,how,[o[0] if o[0]!='steps' else 's%d'%o[1] for o in ops]); print('  at',pl.show(cfg))
    if how!='stuck': break
    lp2=engine.accelerate(cfg,1)
    print('  accel:',None if lp2 is None else (lp2['v'],lp2['inserts'],len(lp2['round'])))
    if lp2 is None: break
    cfg=lp2['resultB']
    print('  resultB',pl.show(cfg))
