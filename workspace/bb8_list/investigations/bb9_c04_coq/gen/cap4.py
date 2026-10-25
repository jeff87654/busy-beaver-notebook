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
def ins(base,big):
    i=0
    while i<len(base) and base[i]==big[i]: i+=1
    d=len(big)-len(base)
    return i, big[i:i+d]
base=to_preESC(D0f_concrete(38,24,3,8,2,[9,13]))
import json
print('BASElen',len(base))
# per-var single-unit (P uses +6 step so divide)
for lbl,a,step in [('P',(38,30,3,8,2,[9,13]),6),('s',(38,24,4,8,2,[9,13]),1),('y',(38,24,3,9,2,[9,13]),1),('t',(38,24,3,8,3,[9,13]),1)]:
    big=to_preESC(D0f_concrete(*a)); pos,blk=ins(base,big)
    print(lbl,'pos',pos,'perunit',len(blk)//step,'blk',blk[:max(3,len(blk)//step*2)])
# dump base as a compact RLE for manual assembly
import itertools
def rle(xs):
    out=[]
    i=0
    while i<len(xs):
        j=i
        while j<len(xs) and xs[j]==xs[i]: j+=1
        out.append((xs[i],j-i)); i=j
    return out
print('BASE', base)
