import sys
import planner9 as pl
from planner9 import mkrun, V, BLANK, drive
ONE=(1,)
Rv={'r':1}; Jv={'j':1}
start=('A',[1,1]+mkrun(ONE,Rv)+[0,V('Y')],[0,0]+mkrun((0,),Jv)+[V('z')],'>')
target=('A',mkrun(ONE,Rv)+[0,1,1,0,V('Y')],[0]+mkrun((0,),Jv)+[V('z')],'>')
drive('LOOP',start,target,matchers=(),maxev=300,verbose=True)
