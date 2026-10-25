import sys
import planner8 as pl
from planner8 import mkrun, V, BLANK, drive
ACT='1RB1LG_0RC0LB_1RD0LA_1LE0RH_1RF1RE_0LA0LG_1LC1LA_---0RE'
pl.set_tm(ACT)
U=(1,1); O=(1,)
L=[1,1,1,1]+mkrun(U,{'u':1})+[0,0]+mkrun(O,{'j':1})+[BLANK]
R=[1]+mkrun(O,{'m':1})+[BLANK]
L2=[1,1,1,1]+mkrun(U,{'u':1})+[0,0,1]+mkrun(O,{'j':1})+[BLANK]
R2=mkrun(O,{'m':1})+[BLANK]
drive('LOOP3',('F',L,R,'>'),('F',L2,R2,'>'),maxev=60)
