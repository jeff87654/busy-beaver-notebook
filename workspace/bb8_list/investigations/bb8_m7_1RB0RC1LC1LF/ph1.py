import sys
import planner8 as pl
from planner8 import mkrun, V, BLANK, drive
M='1RB0RC_1LC1LF_1RD0LB_1RA1LE_1LG0LC_0LG1LE_0RH1RC_0RA---'
pl.set_tm(M)
U=(0,1,0)
Bv={'b':1}; Av={'a':1}
start=('G',[BLANK],[0]+mkrun(U,Bv,1)+[1,0,0]+[0,1,0]+mkrun(U,Av)+[1,0,0,V('l')],'>')
target=('G',[BLANK],[0]+mkrun(U,Bv,2)+[1,0,0]+mkrun(U,Av)+[1,0,0,V('l')],'>')
drive('R1',start,target,matchers=(),maxev=300,verbose=True)
