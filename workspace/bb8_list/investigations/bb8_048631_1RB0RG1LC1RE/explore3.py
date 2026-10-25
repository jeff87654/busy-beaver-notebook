import sys
import planner8 as pl
from planner8 import mkrun, V, BLANK, drive
ACT = '1RB0RA_0RC0RD_0LD---_1RE0LF_1RF1RD_1LE0LG_1LF1LH_0RA0LG'
pl.set_tm(ACT)
U = (0, 1)
# R3, b = k+r+1: E> 0 1 1 (01)^(k+r+1) 0 0^k 0 0 1 (01)^y l
R = [0, 1, 1] + mkrun(U, {'k': 1, 'r': 1}, 1) + [0] + mkrun((0,), {'k': 1}) + [0, 0, 1] + mkrun(U, {'y': 1}) + [V('l')]
drive('R3', ('E', [BLANK], R, '>'), None, matchers=(), maxev=int(sys.argv[1]) if len(sys.argv)>1 else 60)
