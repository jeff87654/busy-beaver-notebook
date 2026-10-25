import sys
sys.path.insert(0,'.')
import planner8 as pl
from planner8 import drive, BLANK, mkrun, V, lin
TM='1RB0RH_0LC1LF_1LE0RD_1RC---_0RG0LF_0LB1RA_1RH1RD_0LE1RD'
pl.set_tm(TM)
W=[2,2,3,2,3]
PRE={'A':[1,2,3,2,3],'B':[2,1,3]}
def cells(bs):
    out=[]
    for b in bs: out+= [1]*b+[0]
    return out
BODY=cells(W)
ROT=[0]+BODY[:-1]
def family(phase,k1,k2,c,var='n'):
    """tape = PRE[phase] ++ W5^(coef*var+const) ++ W[:c], head C on blank after last block (c in 0..4).
    Count = coef*var + const where const>=0 is peeled into concrete cells."""
    pre=cells(PRE[phase]); post=cells(W[:c])
    phys=pre[:-1]
    # const copies of ROT go right after pre, in physical order; the variable run sits to the right of those? 
    # physical order: pre[:-1], rot^(var*coef+const), tail ; the run commutes with the const part (same block)
    tail=([0]+post[:-1]) if c>0 else []
    # stream: nearest head first
    L=[]
    L+= list(reversed(tail))
    rotrev=tuple(reversed(ROT))
    # run of coef*var, then const copies, in stream order: all copies identical so order irrelevant for stream
    toks=[]
    for _ in range(k1): toks+=list(rotrev)
    toks.append(('run',rotrev,lin({var:1})))
    for _ in range(k2): toks+=list(rotrev)
    L+=toks
    L+=list(reversed(phys))+[BLANK]
    return ('C',pl.norm_side(L),[BLANK],'>')
def m_of(phase,n,c): return 5*n+c
if __name__=='__main__':
    cfg=family('B',1,3,0)
    print(pl.show(cfg))
