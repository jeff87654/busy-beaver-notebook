import sys
from cfgs import *
pl.set_tm(TM1)
rest=[V('l')]
start=mk(2,'b',1,4,'a',1,rest)       # b run 3b+2 ; a+1 : 3a+4
target=mk(8,None,0,1,'a',1,rest) if False else None
tg=('B',SUF+[0,1]*2+mkrun(T3,{'b':2})+[0,1]*0,[BLANK],'>')
target=('B',SUF+[0,1,0,1]+mkrun(T3,{'b':2},0)+[0,1,0,1]*0,[BLANK],'>')
# target b' = 2b+2 : 3b'+2 = 6b+8 -> T3^(2b+2) + (01)^2 ; a'=a : 3a+1
L=SUF+[0,1,0,1]+mkrun(T3,{'b':2},2)+[1]+[0,1]+mkrun(T3,{'a':1})+[1]+rest
target=('B',L,[BLANK],'>')
script,cfg=drive('R1',start,target,maxev=60)
