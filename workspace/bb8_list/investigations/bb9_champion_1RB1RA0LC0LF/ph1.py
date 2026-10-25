import sys
import planner9 as pl
from planner9 import mkrun, V, BLANK, drive
ONE=(1,)
Bv={'b':1}; Yv={'y':1}
def K(q,Rstruct): return (q,[BLANK],Rstruct,'<')
start=K('D',[1]+mkrun(ONE,Bv)+[0, 0,1]+mkrun(ONE,Yv)+[V('t')])
target=K('D',[1,1,0,1,1]+mkrun(ONE,Bv)+[0]+mkrun(ONE,Yv)+[V('t')])
drive('R2',start,target,matchers=(),maxev=300,verbose=True)
