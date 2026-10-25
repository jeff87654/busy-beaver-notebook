import sys
from cfgs import *
pl.set_tm(TM1)
U=(0,1); UR=(1,0)
ctx=[0,1,0,1,1,0,1]
start=('F',[1,1]+mkrun(U,{'q':1},4)+[1,V('l')],[0]+mkrun(UR,{'m':1})+ctx+[BLANK],'>')
script,cfg=drive('MID',start,None,maxev=60)
