import sys
import planner8 as pl
from planner8 import drive, mkrun, V, BLANK
import phases884 as P
pl.set_tm(P.TM)
O=(1,)
L=[0]+mkrun(O,{'i':1})+[BLANK]
drive('CLOOP',('C',L,[1]+mkrun(O,{'m':1})+[BLANK],'>'),('C',[0,1]+mkrun(O,{'i':1})+[BLANK],mkrun(O,{'m':1})+[BLANK],'>'),maxev=30)
drive('CEND',('C',L,[BLANK],'>'),None,maxev=30)
