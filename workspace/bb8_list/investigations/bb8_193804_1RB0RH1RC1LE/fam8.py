import sys
sys.path.insert(0,'.')
import planner8 as pl
from planner8 import drive, BLANK, mkrun, V, lin, norm_side
from pipe import pipe_matcher
TM='1RB0RH_1RC1LE_0LD0RF_---1RE_1LB0LB_1RA0RG_0LC1RF_0LG1LA'
pl.set_tm(TM)
def run(block,var): return ('run',tuple(block),lin({var:1}))
def ones(n): return [1]*n
def Xcfg(m_const, rest, lft=None):
    """X: head B at left end, tape 00 1^(4(m+m_const)+1) <rest>"""
    R=[0,0,1]+[1]*(4*m_const)+[run((1,1,1,1),'m')]+rest
    return ('B',norm_side([BLANK]),norm_side(R),'>')
if __name__=='__main__':
    # R1: (a; w+1 : ...) -> (a+4; w ...)
    rest_s=[0,1,1,run((1,),'w'),0,V('r')]
    rest_t=[0,1,run((1,),'w'),0,V('r')]
    s=Xcfg(0,rest_s); t=Xcfg(1,rest_t)
    print(pl.show(s)); print(pl.show(t))
    script,end=drive('R1',s,t,matchers=[pipe_matcher()],maxev=400,verbose=True)
