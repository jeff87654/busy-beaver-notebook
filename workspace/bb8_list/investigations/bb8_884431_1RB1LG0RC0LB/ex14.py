import sys
import planner8 as pl
from planner8 import mkrun, V, BLANK, drive
ACT='1RB1LG_0RC0LB_1RD0LA_1LE0RH_1RF1RE_0LA0LG_1LC1LA_---0RE'
pl.set_tm(ACT)
U=(1,1); O=(1,); Z=(0,)
# S2c: (1111 (11)^u 0 0 1^(j+3)) F> blank -> B> 0 0 0 0^(j+3)... 
L=[1,1,1,1]+mkrun(U,{'u':1})+[0,0]+mkrun(O,{'j':1},3)+[BLANK]
T=[0,0,0]+mkrun(Z,{'j':1},3)+[1]+mkrun(U,{'u':1})+[1,1,1,1,BLANK]
drive('S2c',('F',L,[BLANK],'>'),('B',[BLANK],T,'>'),maxev=60)
