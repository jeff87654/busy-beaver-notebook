import sys
import planner8 as pl
from planner8 import mkrun, V, BLANK, drive
ACT='1RB1LG_0RC0LB_1RD0LA_1LE0RH_1RF1RE_0LA0LG_1LC1LA_---0RE'
pl.set_tm(ACT)
U=(1,1)
k=int(sys.argv[1])
R=[0,0,0]+mkrun(U,{'b':1})+[0]*(k+2)+[1,1]+mkrun(U,{'y':1})+[V('rr')]
T=[0]*(k+4)+mkrun(U,{'b':1},2)+[0]+mkrun(U,{'y':1})+[V('rr')]
drive('R3 k=%d'%k,('B',[BLANK],R,'>'),('B',[BLANK],T,'>'),maxev=80)
