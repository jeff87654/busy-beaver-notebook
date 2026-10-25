import sys
from genc import *
pl.set_tm(phc.TMS['1'])
U=phc.U;UR=phc.UR;CTX=phc.CTX
start=('B',phc.SUF+mkrun(U,{'n':1},4)+[1]+mkrun(U,{'q':1},4)+[1,V('l')],[BLANK],'>')
script,cfg=drive('R1',start,None,maxev=60)
