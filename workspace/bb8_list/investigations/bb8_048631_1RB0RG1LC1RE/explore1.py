import sys
import planner8 as pl
from planner8 import mkrun, V, BLANK, drive
ACT = '1RB0RA_0RC0RD_0LD---_1RE0LF_1RF1RD_1LE0LG_1LF1LH_0RA0LG'
pl.set_tm(ACT)
U = (0, 1)
# R1: E> 0 1 1 (01)^b 0 0 1 (01)^a l  ->  E> 0 1 1 (01)^(b+2) 0 (01)^a l
R = [0, 1, 1] + mkrun(U, {'b': 1}) + [0, 0, 1] + mkrun(U, {'a': 1}) + [V('l')]
T = [0, 1, 1] + mkrun(U, {'b': 1}, 2) + [0] + mkrun(U, {'a': 1}) + [V('l')]
drive('R1', ('E', [BLANK], R, '>'), ('E', [BLANK], T, '>'), matchers=(), maxev=60)
