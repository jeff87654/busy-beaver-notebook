import sys, os, time
sys.path.insert(0,'C:/Users/jeffr/Downloads/bb8/bb8_list/investigations/bb8_891716_1RB0LD0LC1RB')
from rules891 import *
import engine
pl.set_tm(TM)
nm=sys.argv[1]
s,t=rules()[nm]
tc=pl.canon(t)
cfg=s
for i in range(int(sys.argv[2]) if len(sys.argv)>2 else 6):
    t0=time.time()
    ops,cfg,how=engine.run_until_stuck(cfg,tc,target=t)
    print('stage',i,how,'%.1fs'%(time.time()-t0),'steps',sum(o[1] for o in ops if o[0]=='steps'),[o[0] if o[0]!='steps' else 's%d'%o[1] for o in ops])
    print('  at',pl.show(cfg))
    if how!='stuck': break
    t0=time.time()
    lp=engine.accelerate(cfg,1)
    print('  accelerate %.1fs'%(time.time()-t0), None if lp is None else (lp['v'],lp['inserts'],'nested' if len(lp['round'])>1 else ''))
    if lp is None: break
    cfg=engine.subst(lp['resultB'],lp['v2'],(),0) if False else lp['result']
    print('  after loop(full):',pl.show(cfg))
