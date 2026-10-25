import sys
import planner8 as pl
from planner8 import mkrun, V, BLANK, drive
ACT = '1RB1LG_0RC0RH_1RD0RE_1LE---_1RF1RE_0LA0LG_1LH1LA_0RA0LA'
pl.set_tm(ACT)
U = (1,1)
R = [0,0,1,1] + mkrun(U, {'c': 1}) + [0, 1, V('l')]
T = [0,0,1,1,1,1] + mkrun(U, {'c': 1}) + [0, V('l')]
drive('R1', ('A', [BLANK], R, '>'), ('A', [BLANK], T, '>'), matchers=(), maxev=60)
