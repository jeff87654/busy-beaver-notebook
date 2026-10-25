import planner8 as pl
from planner8 import BLANK, V
from common import TB, run
import sys; sys.path.insert(0,'../eg'); sys.path.insert(0,'../tools')
from ktparse import parse
def D0f_concrete(L,P,s,y,t,ltoks):
    def D(x): return [1]+[0,1]*x
    lcells=[]
    for d in ltoks: lcells+=D(d)
    lcells+=[1,1]
    return ('B',[1,0,0,1]+list(TB)*t+[1,1]+[1]*L+[0,0,1]*P+[1,1,0]+[0,1]*y+[1,0,1]+[0,1]*s+[1]+lcells,[BLANK],'>')
def to_preESC(cfg,maxsteps=400000):
    for i in range(maxsteps):
        q,Lc,Rc,mode=cfg
        if q=='B' and mode=='>' and (Rc==[BLANK] or all(c==BLANK for c in Rc)) and Lc[:4]==[1,0,0,1] and i>50:
            w=''.join(str(c) for c in reversed([c for c in Lc if c!=BLANK])).lstrip('0'); r=parse(w)
            if r and r[1] and r[2]==1 and r[3]==2:
                toks=r[1]
                for j in range(len(toks)-3):
                    if toks[j:j+4]==[2,8,6,7] and all(x==1 for x in toks[j+4:]): return Lc
        try: cfg=pl.step(cfg)
        except pl.Halted: return None
    return None
base=to_preESC(D0f_concrete(38,24,3,8,2,[9,13]))   # p=1(P=24),s=3,y=8,t=2,l=[9,13]; near K=9
# segment boundaries (from cap4): TB region base[4:76]=(TB)^9; near base[88:115]=(101)^9; y base[163:179]=(01)^8; s base[180:186]=(01)^3
assert base[4:12]==list(TB) and base[88:91]==[1,0,1] and base[163:165]==[0,1] and base[180:182]==[0,1], "boundary check"
print('seg1', base[76:88]); print('seg2', base[115:163]); print('seg3', base[179:180]); print('after s', base[186:195])
# find where l starts after the '1' separator at 186
print('base tail from 186:', base[186:])
