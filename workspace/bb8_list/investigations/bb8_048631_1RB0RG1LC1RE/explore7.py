import sys
import planner8 as pl
from planner8 import mkrun, V, BLANK, drive
ACT = '1RB0RA_0RC0RD_0LD---_1RE0LF_1RF1RD_1LE0LG_1LF1LH_0RA0LG'
pl.set_tm(ACT)
U = (0, 1)
L = mkrun((1, 0, 0), {'j': 1}) + [1, BLANK]
T = [0,1,1] + mkrun((0,0,1), {'j': 1}) + [0,0,1,0,1,BLANK]
drive('END4', ('H', L, [0, 1, BLANK], '>'), ('E', [BLANK], T, '>'), matchers=(), maxev=40)
