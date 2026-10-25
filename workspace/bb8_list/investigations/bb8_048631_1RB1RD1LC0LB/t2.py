import os
os.environ['BB8TM']="1RB1RD_1LC0LB_1RA0LB_0RE0RG_1RA1LF_1LG0LH_1RD0LF_1LF---"
import planner_b as P
from planner_b import C, BLANK as BL
Z=[P.V('z')]
for (q,lb,rb) in (('E',(0,1),(1,0)),('D',(1,0),(0,1))):
    start=(q,[('run',lb,C(2,a=1)),BL],[('run',rb,C(2,c=1))]+Z,'>')
    tgt=(q,[('run',lb,C(5,a=1)),BL],[('run',rb,C(1,c=1))]+Z,'>')
    try:
        script,end=P.drive('TL1'+q,start,tgt,maxev=300,verbose=True)
        print(script[-1])
    except Exception as e: print('ERR',e)
