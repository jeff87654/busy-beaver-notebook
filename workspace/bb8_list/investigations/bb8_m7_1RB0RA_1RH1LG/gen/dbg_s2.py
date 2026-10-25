from gen_t1 import *
import mexp
from mexp import show
s,t=STAGES['S2']
print('START', show(s)[:300])
ops,cfg,how=mexp.run_stuck(s,t)
print(how, show(cfg)[:600])
# split b = S b'
from mexp import subst
a=cfg
for name in ['b']:
    c1=subst(a,'b',(('b1',1),),1)
    ops2,cfg2,how2=mexp.run_stuck(c1,subst(t,'b',(('b1',1),),1))
    print('after split', how2, show(cfg2)[:700])
print('--- find_loop verbose')
lp=mexp.find_loop(cfg,2,verbose=True)
print('loop', lp is not None)
