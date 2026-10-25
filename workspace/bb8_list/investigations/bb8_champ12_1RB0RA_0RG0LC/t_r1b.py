import sys
from cfgs import *
pl.set_tm(TM1)
U=(0,1)
# start: B at blank, left = SUF (01)^(n+3) 1 (01)^(q+4) 1 l  ; no target: run until stuck
start=('B',SUF+mkrun(U,{'n':1},3)+[1]+mkrun(U,{'q':1},4)+[1,V('l')],[BLANK],'>')
script,cfg=drive('R1',start,None,maxev=60)
