import sys
import planner8 as pl
from planner8 import mkrun, V, BLANK, drive
ACT='1RB1LG_0RC0LB_1RD0LA_1LE0RH_1RF1RE_0LA0LG_1LC1LA_---0RE'
pl.set_tm(ACT)
U=(1,1)
# LOOP: (0 1 1 1 l) H> (11)^b 1 1 1 0 0 rr -> (0 1 1 1 1 l) H> (11)^b 1 1 1 0 rr
L=[0,1,1,1,V('l')]
R=mkrun(U,{'b':1})+[1,1,1,0,0,V('rr')]
L2=[0,1,1,1,1,V('l')]
R2=mkrun(U,{'b':1})+[1,1,1,0,V('rr')]
drive('LOOP',('H',L,R,'>'),('H',L2,R2,'>'),maxev=40)
