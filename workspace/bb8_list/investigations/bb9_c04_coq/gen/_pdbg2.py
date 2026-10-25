from common import *
from shapes import *
import mexp, time, sys
L=int(sys.argv[1])
S=('B',[1,0,0,1, run(TB,t=1), 1,1] + [1]*L + [run((0,0,1),P=1)] + [1,1,0]
    + [run((0,1),y=1)] + [1,0,1] + [run((0,1),s=1)] + [1, V('l')], [BLANK],'>')
cfg=S; t0=time.time()
for k in range(40):
    ops,cfg,how=mexp.run_stuck(cfg,None,budget=3000000)
    print(k,how,'%.1fs'%(time.time()-t0),pl.show(cfg)[:95]); sys.stdout.flush()
    if how in('halt','target'): break
    lp=mexp.find_loop(cfg,2)
    if lp is None: print('NO LOOP->split'); break
    cfg=lp.after()
