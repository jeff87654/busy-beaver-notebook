import sys
import planner9 as pl
from planner9 import mkrun, V, BLANK, drive
ONE=(1,)
Bv={'b':1}; Yv={'y':1}; Kv={'k':1}
def K(q,Rstruct): return (q,[BLANK],Rstruct,'<')
start=K('D',[1]+mkrun(ONE,Bv)+[0]+mkrun((0,),Kv)+[0,1]+mkrun(ONE,Yv)+[V('t')])
drive('R3',start,None,matchers=(),maxev=300,verbose=True)
