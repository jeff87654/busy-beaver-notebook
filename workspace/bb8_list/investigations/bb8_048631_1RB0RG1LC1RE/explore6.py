import sys
import planner8 as pl
from planner8 import mkrun, V, BLANK, drive
ACT = '1RB0RA_0RC0RD_0LD---_1RE0LF_1RF1RD_1LE0LG_1LF1LH_0RA0LG'
pl.set_tm(ACT)
U = (0, 1)
# TR: E> 0 1 1 (01)^b 0 0 0 rr  ->  L = 1 ; H> 0 1 (01)^b 0 0 rr
R = [0, 1, 1] + mkrun(U, {'b': 1}) + [0, 0, 0, V('rr')]
T = [0, 1] + mkrun(U, {'b': 1}) + [0, 0, V('rr')]
drive('TR', ('E', [BLANK], R, '>'), ('H', [1, BLANK], T, '>'), matchers=(), maxev=60)
