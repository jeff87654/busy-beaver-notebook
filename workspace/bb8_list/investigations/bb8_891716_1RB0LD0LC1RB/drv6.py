import sys, os, time
sys.path.insert(0,'C:/Users/jeffr/Downloads/bb8/bb8_list/investigations/bb8_891716_1RB0LD0LC1RB')
from rules891 import *
import engine
pl.set_tm(TM)
nm=sys.argv[1]
s,t=rules()[nm]
cfg=s
for i in range(10):
    ops,cfg,how=engine.run_until_stuck(cfg,None,target=t)
    if how!='stuck': print('end',how); break
    lp=engine.accelerate(cfg,1)
    if lp is None: break
    cfg=lp['result']
print('STUCK AT',pl.show(cfg))
for depth in (1,2,3):
    t0=time.time()
    try:
        lp=engine.accelerate(cfg,depth)
    except Exception as e:
        print('depth',depth,'EXC',type(e).__name__,str(e)[:200]); continue
    print('depth',depth,'%.1fs'%(time.time()-t0), None if lp is None else (lp['v'],lp['inserts'],[r[0] for r in lp['round']]))
print('--- peel rounds')
S=cfg
for it in range(4):
    v='k' if it==0 else engine.candidates(S)[0]
    v2=engine.fresh(v)
    Pc=engine.subst(S,v,((v2,1),),1)
    try:
        ops,C2,how=engine.run_until_stuck(Pc,None,budget=20000)
    except Exception as e:
        print('EXC',e); break
    print(it,'ops',[o[0] if o[0]!='steps' else 's%d'%o[1] for o in ops],how)
    print('  from ',pl.show(S)); print('  after',pl.show(C2))
    S=C2
print('--- one outer round with inner loops from the E config')
S=C0 if 'C0' in globals() else None
S=cfg
v='k'; v2=engine.fresh(v)
Pc=engine.subst(S,v,((v2,1),),1)
ops,S,how=engine.run_until_stuck(Pc,None)
print('S (E config) =',pl.show(S))
v=engine.candidates(S)[0]; print('var',v)
v2=engine.fresh(v)
S1=engine.subst(S,v,((v2,1),),0)
Pc=engine.subst(S,v,((v2,1),),1)
ops,C,how=engine.run_until_stuck(Pc,None)
print('R0',[o[0] if o[0]!='steps' else 's%d'%o[1] for o in ops],how); print('  ',pl.show(C))
for i in range(6):
    m=engine.match_shift(S1,C)
    print('  match',m)
    if m is not None: break
    sub=engine.accelerate(C,2)
    if sub is None:
        print('  no inner loop'); break
    print('  inner loop on',sub['v'],sub['inserts'],'nested' if len(sub['round'])>1 else '')
    ops,C,how=engine.run_until_stuck(sub['result'],None)
    print('R%d'%(i+1),[o[0] if o[0]!='steps' else 's%d'%o[1] for o in ops],how); print('  ',pl.show(C))
    if how!='stuck': break
