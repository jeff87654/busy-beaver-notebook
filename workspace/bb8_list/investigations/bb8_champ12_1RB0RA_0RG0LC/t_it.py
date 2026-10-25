import sys
from cfgs import *
pl.set_tm(TM1)
U=(0,1)   # nearest-first unit of left stream  (10 as written left-to-right)
UR=(1,0)  # right stream unit (10 left-to-right)
ctx=[0,1,0,1,1,0,1]
# IT: left: [1] + (01)^(k+1) + rest ; head F on right: 0 (10)^m ctx...
start=('F',[1]+mkrun(U,{'k':1},1)+[V('l')],[0]+mkrun(UR,{'m':1})+ctx+[BLANK],'>')
target=('F',[1]+mkrun(U,{'k':1})+[V('l')],[0]+mkrun(UR,{'m':1},2)+ctx+[BLANK],'>')
script,cfg=drive('IT',start,target,maxev=60)
