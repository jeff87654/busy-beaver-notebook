import sys
import planner8 as pl
from planner8 import mkrun, V, BLANK, drive
ACT='1RB1LG_0RC0LB_1RD0LA_1LE0RH_1RF1RE_0LA0LG_1LC1LA_---0RE'
pl.set_tm(ACT)
U=(1,1); O=(1,)
# E1: (0 1 1 1 (11)^u) H> (11)^b 1 1 1 0 1 blank  ->  M1 = B> 0 0 0 1 (11)^u 0 (11)^b 1^6 blank
L=[0,1,1,1]+mkrun(U,{'u':1})+[BLANK]
R=mkrun(U,{'b':1})+[1,1,1,0,1,BLANK]
T=[0,0,0,1]+mkrun(U,{'u':1})+[0]+mkrun(U,{'b':1})+[1,1,1,1,1,1,BLANK]
drive('E1->M1',('H',L,R,'>'),('B',[BLANK],T,'>'),maxev=60)
