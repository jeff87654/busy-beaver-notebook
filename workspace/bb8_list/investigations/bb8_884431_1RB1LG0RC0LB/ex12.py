import sys
import planner8 as pl
from planner8 import mkrun, V, BLANK, drive
ACT='1RB1LG_0RC0LB_1RD0LA_1LE0RH_1RF1RE_0LA0LG_1LC1LA_---0RE'
pl.set_tm(ACT)
U=(1,1); O=(1,)
R=[0,0,0,1]+mkrun(U,{'u':1})+[0,1,1,1]+mkrun(O,{'r':1})+[BLANK]
drive('M2',('B',[BLANK],R,'>'),None,maxev=int(sys.argv[1]))
