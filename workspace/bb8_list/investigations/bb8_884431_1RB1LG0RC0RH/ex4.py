import sys
import planner8 as pl
from planner8 import mkrun, V, BLANK, drive
ACT = '1RB1LG_0RC0RH_1RD0RE_1LE---_1RF1RE_0LA0LG_1LH1LA_0RA0LA'
pl.set_tm(ACT)
U = (1,1)
R = [1,1] + mkrun(U, {'r': 1}) + [0, 0, V('rr')]
L = [0,1,1,0,V('l')]
drive('LOOP', ('C', L, R, '>'), None, matchers=(), maxev=60)
