"""Waypoint configurations for the R3 rules of 891716 (engine form, stream order: nearest the head first)."""
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, 'C:/Users/jeffr/Downloads/bb8/bb8_list/autoproof')
from rules891 import *
import planner8 as pl
from planner8 import BLANK, mkrun, V
import engine, validate
pl.set_tm(TM)
R = rules()
DIG = [1] + mkrun((0, 1), {'y': 1}) + [0, V('t')]     # left of the zeros: the digit (01)^(y+1) minus its first 0, then t

def PS(zc, zv, bc, bv, dc, dv, tail=DIG, q='E'):
    """pass start: left 1 0^z tail ; head E ; right (0101)^blocks 0 (01)^3 (10101)^d."""
    L = [1] + mkrun((0,), zv, zc) + tail
    Rt = mkrun((0, 1, 0, 1), bv, bc) + [0, 0, 1, 0, 1, 0, 1] + mkrun((1, 0, 1, 0, 1), dv, dc) + [BLANK]
    return (q, pl.norm_side(L), pl.norm_side(Rt), '>')

def chk(s, t, grid, ms=500000):
    bad = []
    for vals in grid:
        r = validate.reaches(s, t, vals, max_steps=ms)
        if r is None:
            bad.append(vals)
    return bad
