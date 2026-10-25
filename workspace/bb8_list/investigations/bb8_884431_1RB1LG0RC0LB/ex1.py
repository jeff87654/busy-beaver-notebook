import sys
import planner8 as pl
from planner8 import mkrun, V, BLANK, drive
ACT='1RB1LG_0RC0LB_1RD0LA_1LE0RH_1RF1RE_0LA0LG_1LC1LA_---0RE'
pl.set_tm(ACT)
U=(1,1)
# R1: B> 0 0 (11)^b 0 11 (11)^a rr  ->  B> 0 0 (11)^(b+2) 0 (11)^a rr
R=[0,0,0]+mkrun(U,{'b':1})+[0]+mkrun(U,{'a':1},1)+[V('rr')]
T=[0,0,0]+mkrun(U,{'b':1},2)+[0]+mkrun(U,{'a':1})+[V('rr')]
drive('R1',('B',[BLANK],R,'>'),('B',[BLANK],T,'>'),maxev=60)
