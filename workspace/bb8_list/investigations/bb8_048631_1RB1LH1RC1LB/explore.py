import sys
import planner8 as pl
from planner8 import mkrun, V, BLANK, drive
pl.set_tm("1RB1LH_1RC1LB_0RD1RE_1LB0LB_1RF0LA_1LG1LF_1RH0LD_---0LE")
def F(k,r,t):  # k,r,t : dicts (var coeffs) + consts handled by caller
    return None
# F(k,r+3,t): 0 1 0 1 1 (001)^k 0 1 1 1 1^r 00 1 1 1^t
Rt = [0,1,0,1,1] + mkrun((0,0,1),{'k':1}) + [0,1,1,1] + mkrun((1,),{'r':1}) + [0,0,1,1] + mkrun((1,),{'t':1})
start=('B',[BLANK],Rt+[BLANK],'>')
if __name__=="__main__":
    script,cfg=drive('cycle',start,None,maxev=60,verbose=True)
