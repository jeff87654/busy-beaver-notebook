import sys
import planner8 as pl
from planner8 import mkrun, V, BLANK, drive
ACT='1RB1LG_0RC0LB_1RD0LA_1LE0RH_1RF1RE_0LA0LG_1LC1LA_---0RE'
pl.set_tm(ACT)
U=(1,1); O=(1,)
L=[1,1,1,1]+mkrun(U,{'u':1})+[0,0]+mkrun(O,{'j':1},int(sys.argv[1]))+[BLANK]
drive('ZE',('F',L,[BLANK],'>'),None,maxev=60)
