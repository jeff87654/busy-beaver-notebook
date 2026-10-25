import sys
import planner9 as pl
from planner9 import mkrun, V, BLANK, drive
ONE=(1,)
Sv={'s':1}; Mv={'m':1}; Yv={'y':1}
# L = 1^s (0 1 1)^(m+2)  (blank) ; R = 0 1 1^y t
start=('A',mkrun(ONE,Sv)+mkrun((0,1,1),Mv,2)+[BLANK],[0,1]+mkrun(ONE,Yv)+[V('t')],'>')
# target: D at blank, R' = 1 1 0 1 1 (0 1 1)^m 0 1^(s+2) 0 1^y t
tgt=('D',[BLANK],[1]+mkrun((1,0,1),Mv)+[1,0,1,1,0,1]+mkrun(ONE,Sv)+[1,0]+mkrun(ONE,Yv)+[V('t')],'<')
drive('FINAL',start,tgt,matchers=(),maxev=300,verbose=True)
