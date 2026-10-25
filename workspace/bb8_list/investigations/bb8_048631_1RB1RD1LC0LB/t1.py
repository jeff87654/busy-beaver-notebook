import os
os.environ['BB8TM']="1RB1RD_1LC0LB_1RA0LB_0RE0RG_1RA1LF_1LG0LH_1RD0LF_1LF---"
import planner_b as P
from planner_b import C, BLANK as BL
# E-loop: left 10^(a+2), right 10^(c+2) 01 Z
def cells(b): return tuple(int(x) for x in b)
Z=[P.V('z')]
start=('E',[('run',(0,1),C(2,a=1)),BL],[('run',(1,0),C(2,c=1))]+[0,1]+Z,'>')
tgt=('E',[('run',(0,1),C(5,a=1)),BL],[('run',(1,0),C(1,c=1))]+[0,1]+Z,'>')
script,end=P.drive('TL1',start,tgt,maxev=300,verbose=True)
print(script[-1])
