import sys
import planner8 as pl
from planner8 import mkrun, V, BLANK, drive
ACT='1RB1LG_0RC0LB_1RD0LA_1LE0RH_1RF1RE_0LA0LG_1LC1LA_---0RE'
pl.set_tm(ACT)
U=(1,1)
# FINAL: ([0] 1^(j+3)) H> (11)^b 1 1 1 0 1 1 (11)^y rr  -> ?
L=[0]+mkrun((1,),{'j':1},3)+[BLANK]
R=mkrun(U,{'b':1})+[1,1,1,0,1,1]+mkrun(U,{'y':1})+[V('rr')]
drive('FINAL',('H',L,R,'>'),None,maxev=40)
