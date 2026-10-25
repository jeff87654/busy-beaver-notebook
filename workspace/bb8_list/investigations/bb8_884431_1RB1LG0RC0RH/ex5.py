import sys
import planner8 as pl
from planner8 import mkrun, V, BLANK, drive
ACT = '1RB1LG_0RC0RH_1RD0RE_1LE---_1RF1RE_0LA0LG_1LH1LA_0RA0LA'
pl.set_tm(ACT)
U = (1,1)
j = int(sys.argv[1]) if len(sys.argv)>1 else -1
L = (mkrun((0,1,1),{'j':1}) if j<0 else [0,1,1]*j) + [0,1,BLANK]
R = [1,1] + mkrun(U, {'r': 1}) + [0, 1] + mkrun((1,),{'y':1}) + [V('rr')]
drive('FINAL', ('C', L, R, '>'), None, matchers=(), maxev=60)
