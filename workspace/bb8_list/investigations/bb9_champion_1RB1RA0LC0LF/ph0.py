import sys
import planner9 as pl
from planner9 import mkrun, V, BLANK, drive
ONE=(1,)
Bv={'b':1}; Av={'a':1}
# original orientation: head left of structure; mode '<' ; L=[BLANK], R = structure nearest-first
def K(q,Rstruct): return (q,[BLANK],Rstruct,'<')
start=K('D',[1]+mkrun(ONE,Bv)+[0,1]+mkrun(ONE,Av)+[V('l')])
target=K('D',[1]+mkrun(ONE,{'b':1},3)+[0]+mkrun(ONE,Av)+[V('l')])
drive('R1',start,target,matchers=(),maxev=300,verbose=True)
