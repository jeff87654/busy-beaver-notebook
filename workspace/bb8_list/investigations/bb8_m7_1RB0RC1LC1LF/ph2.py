import sys
import planner8 as pl
from planner8 import mkrun, V, BLANK, drive
M='1RB0RC_1LC1LF_1RD0LB_1RA1LE_1LG0LC_0LG1LE_0RH1RC_0RA---'
pl.set_tm(M)
U=(0,1,0); S=(1,0,0)
start=('G',[BLANK],[0]+mkrun(U,{'B':1},2)+mkrun(S,{'J':1},2)+[0,1,0]+mkrun(U,{'y':1})+[1,0,0,V('l')],'>')
target=('G',[BLANK],[0]+[0,1,0]+mkrun(S,{'J':1},1)+mkrun(U,{'B':1},2)+[1,0,0]+mkrun(U,{'y':1})+[1,0,0,V('l')],'>')
drive('RU',start,target,matchers=(),maxev=300,verbose=True)
