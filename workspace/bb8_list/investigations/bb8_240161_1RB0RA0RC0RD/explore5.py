import sys
import planner8 as pl
from planner8 import mkrun, V, BLANK, drive
ACT = '1RB0RA_0RC0RD_0LD---_1RE0LF_1RF1RD_1LE0LG_1LF1LH_0RA0LG'
pl.set_tm(ACT)
U = (0, 1)
# FINAL: L = (1 0 0)^j 1 ; H> 0 1 (01)^(r+1) 0 0 1 (01)^y rr  ->  E> 0 1 1 (001)^j 0 (01)^(r+3) 0 (01)^y rr
L = mkrun((1, 0, 0), {'j': 1}) + [1, BLANK]
R = [0, 1] + mkrun(U, {'r': 1}, 1) + [0, 0, 1] + mkrun(U, {'y': 1}) + [V('rr')]
T = [0, 1, 1] + mkrun((0, 0, 1), {'j': 1}) + [0] + mkrun(U, {'r': 1}, 3) + [0] + mkrun(U, {'y': 1}) + [V('rr')]
drive('FINAL', ('H', L, R, '>'), ('E', [BLANK], T, '>'), matchers=(), maxev=80)
