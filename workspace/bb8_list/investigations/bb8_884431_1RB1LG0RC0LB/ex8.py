import sys
import planner8 as pl
from planner8 import mkrun, V, BLANK, drive
ACT='1RB1LG_0RC0LB_1RD0LA_1LE0RH_1RF1RE_0LA0LG_1LC1LA_---0RE'
pl.set_tm(ACT)
U=(1,1)
par=int(sys.argv[1])
L=[0,1,1,1]+[1]*par+mkrun(U,{'u':1})+[BLANK]
R=mkrun(U,{'b':1})+[1,1,1,0,1,BLANK]
drive('ZFINAL par=%d'%par,('H',L,R,'>'),None,maxev=int(sys.argv[2]))
