import sys
import planner8 as pl
from planner8 import drive
import phases884 as P
pl.set_tm(P.TM)
st,tg=P.PH['ZONE']
drive('ZONE',st,None,maxev=40)
