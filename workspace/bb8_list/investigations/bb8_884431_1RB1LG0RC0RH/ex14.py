import sys
import planner8 as pl
from planner8 import mkrun, V, BLANK, drive
ACT = '1RB1LG_0RC0RH_1RD0RE_1LE---_1RF1RE_0LA0LG_1LH1LA_0RA0LA'
pl.set_tm(ACT)
L = mkrun((0,1,1),{'t':1}) + [0,1,1,0,1,BLANK]
T = [0,0,1,1,0] + mkrun((1,1,0),{'t':1}) + [1,1,1,1,0,BLANK]
drive('END4', ('C', L, [BLANK], '>'), ('A',[BLANK],T,'>'), matchers=(), maxev=60)
