import idle, sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb8_list\autoproof')
import planner8 as pl
import engine, coqgen
from planner8 import BLANK, V, mkrun
TM = '1RB0RC_1RC0RA_1LD0LB_1LE0LA_0LF---_1RC0LG_1LF1LA'
pl.set_tm(TM)
# left-side stream-order blocks (nearest head first): segment (p,q) = (01)^p (10)^q in tape order
A_ = (1, 0)   # tape block 01 read leftwards
B_ = (0, 1)   # tape block 10 read leftwards
SEP = [1, 1]
def segL(p, q):
    """left-side tokens (nearest first) for tape (01)^p (10)^q ; p,q dicts or ints"""
    out = []
    out += (mkrun(B_, q) if isinstance(q, dict) else list(B_) * q)
    out += (mkrun(A_, p) if isinstance(p, dict) else list(A_) * p)
    return out
def lin(**kw):
    return dict(kw)
def K(segs, tail):
    """K config: segs list of (p,q) from LEFT to RIGHT (last = accumulator); tail = left terminator (BLANK or V('l'))"""
    L = []
    for i, (p, q) in enumerate(reversed(segs)):
        if i > 0: L += SEP
        L += segL(p, q)
    L += [tail]
    return ('A', pl.norm_side(L), [0, 1, BLANK], '>')
def C(var, k=0):
    """count = var + k : returns (dict, const) - use with mkrun via segLc"""
    return (var, k)
