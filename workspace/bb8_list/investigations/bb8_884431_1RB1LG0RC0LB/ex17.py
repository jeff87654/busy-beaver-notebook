import sys
import planner8 as pl
from planner8 import drive, mkrun, V, BLANK
import phases884 as P
pl.set_tm(P.TM)
O=(1,); U=(1,1)
L=[0,1,1,1]+mkrun(U,{'u':1})+[BLANK]
T=[0,0,0,1]+mkrun(U,{'u':1})+[0,1,1,1,1,BLANK]
drive('CEND',('C',L,[BLANK],'>'),('B',[BLANK],T,'>'),maxev=30)
st,tg=P.PH['ZONE']
drive('ZONE1',st,('C',[0,1,1,1,1,BLANK],mkrun(U,{'b':1})+[1,1,1,BLANK],'>'),maxev=30)
