import sys
sys.path.insert(0,'.')
import planner8 as pl
from tmlit import Sim
import tr
from fam import parse
def expand(side, vals):
    out=[]
    for t in side:
        if isinstance(t,int): out.append(t)
        elif t==pl.BLANK: break
        elif t[0]=='run':
            n=sum(c*vals[k] for k,c in t[2])
            out.extend(list(t[1])*n)
        else: raise ValueError(t)
    return out
def k_of(cfg, vals):
    q,L,Rr,mode=cfg
    assert q=='G' and mode=='>' and Rr==[pl.BLANK]
    st=expand(L,vals)
    tape=list(reversed(st))
    w='0000'+''.join(map(str,tape))+'0'
    s=Sim.from_word(tr.TM,w,4+len(tape),'G')
    return parse(s)
