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
S=cfg
for it in range(int(sys.argv[2])):
    v=engine.candidates(S)[0]
    v2=engine.fresh(v)
    Pc=engine.subst(S,v,((v2,1),),1)
    try:
        ops,C2,how=engine.run_until_stuck(Pc,None,budget=40000)
    except Exception as e:
        print('EXC',e); break
    print(it,'ops',[o[0] if o[0]!='steps' else 's%d'%o[1] for o in ops][:12],how)
    print('  after',pl.show(C2))
    # follow: if the head is at an A> run etc, use inner loops greedily
    S=C2
    for _ in range(8):
        lp=engine.accelerate(S,1)
        if lp is None or lp['v']==v2: break
        print('   inner loop on',lp['v'],lp['inserts'])
        ops,S2,how2=engine.run_until_stuck(lp['result'],None,budget=40000)
        print('   ->',[o[0] if o[0]!='steps' else 's%d'%o[1] for o in ops][:10],how2,pl.show(S2)[:300])
        S=S2
        if how2!='stuck': break
