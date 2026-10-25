import sys
import planner8 as pl
from planner8 import mkrun, V, BLANK, drive
ACT='1RB1LG_0RC0LB_1RD0LA_1LE0RH_1RF1RE_0LA0LG_1LC1LA_---0RE'
pl.set_tm(ACT)
U=(1,1); O=(1,); Z=(0,)
# LOOP4
L=[1,1,1,0,0]+mkrun(O,{'q':1})+[BLANK]
R=[0]+mkrun(Z,{'w':1})+[1,1,V('rr')]
L2=[1,1,1,0,0,1]+mkrun(O,{'q':1})+[BLANK]
R2=mkrun(Z,{'w':1})+[1,1,V('rr')]
drive('LOOP4',('F',L,R,'>'),('F',L2,R2,'>'),maxev=60)
# end: w=0
L=[1,1,1,0,0]+mkrun(O,{'q':1})+[BLANK]
R=[1]+mkrun(U,{'u':1})+[1,1,1,1,BLANK]
drive('ZEND',('F',L,R,'>'),None,maxev=60)
