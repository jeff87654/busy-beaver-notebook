import planner8 as pl
from planner8 import BLANK, V
from common import TB, run
import mexp
# correct start: Kx (repeat 1 (S z) ++ [0; S a] ) 1 (S r) t e  == acc (01)^(r+1), m=1(D1), near (101)^(z+1), D0, D(a+1), l
def startsym():
    return ('B',[1,0,0,1,run(TB,t=1),1,1]+[0,1,run((0,1),r=1)]+[1,0,1]+[run((1,0,1),z=1),1,0,1]+[1]+[1,0,1,run((0,1),a=1)]+[1,V('l')],[BLANK],'>')
def startconc(z,a,r,t):
    def rep(b,n): return list(b)*n
    return ('B',[1,0,0,1]+list(TB)*t+[1,1]+[0,1]+[0,1]*r+[1,0,1]+[1,0,1]*(z+1)+[1]+[1,0,1]+[0,1]*a+[1, 1,1]+[BLANK]*0,[BLANK],'>')
# capture halt via single step from concrete
def haltcfg(z,a,r,t):
    cfg=startconc(z,a,r,t)
    for i in range(300000):
        try: cfg=pl.step(cfg)
        except pl.Halted: return cfg
    return None
import engine
# get symbolic halt T by running symbolic start with run_stuck+loops, no split (like HALT before)
cfg=startsym()
for k in range(40):
    ops,cfg,how=mexp.run_stuck(cfg,None,budget=3000000)
    if how=='halt':
        print('HALT state',cfg[0],'mode',cfg[3]); print('L',cfg[1]); print('R',cfg[2]); break
    lp=mexp.find_loop(cfg,2)
    if lp is None:
        print('STUCK->split needed at',pl.show(cfg)[:120])
        _,why=pl.try_crossing(cfg); cand=engine.candidates(cfg, behind_first=bool(why) and why.startswith('left known region'))
        print('cands',cand)
        v=cand[0]; cfg=engine.subst(cfg,v,((mexp.fresh(v),1),),1); print('split',v)
    else: cfg=lp.after()

T=('H',[1,run((0,1),a=1),1,V('l')],
   [1,1,1,1,0,run((1,0,1,0),r=1),0,1,0,1,1,0,1,1,0,1,1,run((0,1,1),z=1),run((1,1,0,0,1,0,0,1),t=1),0,1,BLANK],'<')
S=startsym()
pl.LEMMAS.clear(); mexp.ROT_DONE.clear()
tree=mexp.explore(S,T,splits=0)
print('EXPLORE OK')
