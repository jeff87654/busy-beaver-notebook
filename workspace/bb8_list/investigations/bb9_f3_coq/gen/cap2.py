import planner8 as pl
from planner8 import BLANK
from common import TB
def D0f_concrete(L,P,s,y,t,ltoks):
    def D(x): return [1]+[0,1]*x
    lcells=[]
    for d in ltoks: lcells += D(d)
    lcells += [1,1]  # far 11 boundary (the 0,0 tokens) then blank
    cells=[1,0,0,1]+list(TB)*t+[1,1]+[1]*L+[0,0,1]*P+[1,1,0]+[0,1]*y+[1,0,1]+[0,1]*s+[1]+lcells
    return ('B', cells, [BLANK], '>')
def to_preESC(cfg, maxsteps=300000):
    for i in range(maxsteps):
        q,Lc,Rc,mode=cfg
        # K-moment: state B, mode '>', R is blank, L starts 1001 and has the 6,7 pattern near front
        if q=='B' and mode=='>' and (Rc==[BLANK] or all(c==BLANK for c in Rc)) and Lc[:4]==[1,0,0,1]:
            # check near pattern: after tail+11+acc+Dm, the near zeros then D7 then 6... just return once we pass start
            if i>100: return i, Lc
        try: cfg=pl.step(cfg)
        except pl.Halted: return 'halt', cfg
    return 'budget', cfg
import sys
base_i,base=to_preESC(D0f_concrete(38,24,3,8,2,[9,13]))
print('base step',base_i,'len',len(base))
print('base L', base[:70])
for lbl,a in [('P+6',(38,30,3,8,2,[9,13])),('s+1',(38,24,4,8,2,[9,13])),('y+1',(38,24,3,9,2,[9,13])),('t+1',(38,24,3,8,3,[9,13])),('ltok',(38,24,3,8,2,[9,13,5]))]:
    i,c=to_preESC(D0f_concrete(*a))
    print(lbl,'step',i,'dlen',(len(c)-len(base)) if isinstance(i,int) else i)
