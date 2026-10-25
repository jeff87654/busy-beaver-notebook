import sys
import planner8 as pl
from planner8 import mkrun, V, BLANK, drive
ACT = '1RB0RA_0RC0RD_0LD---_1RE0LF_1RF1RD_1LE0LG_1LF1LH_0RA0LG'
pl.set_tm(ACT)
U = (0, 1)
which = sys.argv[1]
if which == 'R2':   # K(y+1::t; 0; b), b>=1 written b+1
    R = [0, 1, 1] + mkrun(U, {'b': 1}) + [0, 0, 0, 1] + mkrun(U, {'y': 1}) + [V('l')]
elif which == 'R3':  # K(0^(k+1) ++ y+1::t; 0; b)
    R = [0, 1, 1] + mkrun(U, {'b': 1}) + [0] + mkrun((0,), {'k': 1}) + [0, 0, 1] + mkrun(U, {'y': 1}) + [V('l')]
drive(which, ('E', [BLANK], R, '>'), None, matchers=(), maxev=int(sys.argv[2]) if len(sys.argv)>2 else 60)
