import planner8 as pl
from planner8 import BLANK
from common import TB
import sys; sys.path.insert(0,'../eg'); sys.path.insert(0,'../tools')
from ktparse import parse
def D0f_concrete(L,P,s,y,t,ltoks):
    def D(x): return [1]+[0,1]*x
    lcells=[]
    for d in ltoks: lcells+=D(d)
    lcells+=[1,1]
    return ('B',[1,0,0,1]+list(TB)*t+[1,1]+[1]*L+[0,0,1]*P+[1,1,0]+[0,1]*y+[1,0,1]+[0,1]*s+[1]+lcells,[BLANK],'>')
def toks_of(Lc):
    # far->near word = reversed nearest-first cells
    w=''.join(str(c) for c in reversed([c for c in Lc if c!=BLANK])).lstrip('0')
    r=parse(w)
    return r
def to_preESC(cfg,maxsteps=400000):
    for i in range(maxsteps):
        q,Lc,Rc,mode=cfg
        if q=='B' and mode=='>' and (Rc==[BLANK] or all(c==BLANK for c in Rc)) and Lc[:4]==[1,0,0,1] and i>50:
            r=toks_of(Lc)
            if r:
                far,toks,m,rr,t=r
                # pre-ESC: toks far->near end with 2,8,6,7 then all 1s, m=1,r=2
                if m==1 and rr==2 and 7 in toks:
                    idx=None
                    for j in range(len(toks)-3):
                        if toks[j:j+4]==[2,8,6,7] and all(x==1 for x in toks[j+4:]):
                            idx=j; break
                    if idx is not None:
                        return i, Lc, (toks, m, rr, t)
        try: cfg=pl.step(cfg)
        except pl.Halted: return 'halt',cfg,None
    return 'budget',cfg,None
bi,base,binfo=to_preESC(D0f_concrete(38,24,3,8,2,[9,13]))
print('base step',bi,'info',binfo if binfo else None)
if isinstance(bi,int):
    print('base L len',len(base))
    for lbl,a in [('P+6',(38,30,3,8,2,[9,13])),('s+1',(38,24,4,8,2,[9,13])),('y+1',(38,24,3,9,2,[9,13])),('t+1',(38,24,3,8,3,[9,13])),('ltok',(38,24,3,8,2,[9,13,5]))]:
        i,c,_=to_preESC(D0f_concrete(*a))
        print(lbl,'step',i,'dlen',(len(c)-len(base)) if isinstance(i,int) else i)
