import sys, os, time
sys.path.insert(0,'C:/Users/jeffr/Downloads/bb8/bb8_list/investigations/bb8_891716_1RB0LD0LC1RB')
from rules891 import *
import engine
pl.set_tm(TM)
nm=sys.argv[1]
s,t=rules()[nm]
cfg=s
# advance through loops until the stuck point where accelerate returns None
for i in range(10):
    ops,cfg,how=engine.run_until_stuck(cfg,None,target=t)
    if how!='stuck': print('end',how); break
    lp=engine.accelerate(cfg,1)
    if lp is None: break
    cfg=lp['result']
print('STUCK AT',pl.show(cfg))
for v in engine.candidates(cfg):
    S=cfg
    v2=engine.fresh(v)
    Pc=engine.subst(S,v,((v2,1),),1)
    print('peeled',v,pl.show(Pc))
    ops,C,how=engine.run_until_stuck(Pc,None)
    print(' ops',[o[0] if o[0]!='steps' else 's%d'%o[1] for o in ops],how)
    print(' after',pl.show(C))
print('---- iterate peel')
S=C
for it in range(4):
    v=engine.candidates(S)[0]
    v2=engine.fresh(v)
    Pc=engine.subst(S,v,((v2,1),),1)
    ops,C2,how=engine.run_until_stuck(Pc,None)
    print(it,'peel',v,'ops',[o[0] if o[0]!='steps' else 's%d'%o[1] for o in ops],how)
    print('  from ',pl.show(S)); print('  after',pl.show(C2))
    lp=engine.try_loop(S,v,1)
    print('  try_loop', None if lp is None else (lp['inserts'],len(lp['round'])))
    S=C2
