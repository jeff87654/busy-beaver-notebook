import sys
import planner8 as pl
from planner8 import mkrun, V, BLANK, drive
ACT='1RB1LG_0RC0LB_1RD0LA_1LE0RH_1RF1RE_0LA0LG_1LC1LA_---0RE'
pl.set_tm(ACT)
U=(1,1)
# R2: K(x+1::t; 0; b) = B> 000 (11)^b 0 0 (11)^(x+1) rr -> K(x::t; b+2; 0) = B> 000 0 (11)^(b+2) 0 (11)^x rr   [rr = 0 (11)^.. ]
R=[0,0,0]+mkrun(U,{'b':1})+[0,0,1,1]+mkrun(U,{'x':1})+[V('rr')]
T=[0,0,0]+[0]+mkrun(U,{'b':1},2)+[0]+mkrun(U,{'x':1})+[V('rr')]
drive('R2',('B',[BLANK],R,'>'),('B',[BLANK],T,'>'),maxev=60)
