import sys
import planner8 as pl
from planner8 import mkrun, V, BLANK, drive, show, step, head, Stuck
ACT = '1RB1LG_0RC0RH_1RD0RE_1LE---_1RF1RE_0LA0LG_1LH1LA_0RA0LA'
pl.set_tm(ACT)
r=int(sys.argv[1]); j=int(sys.argv[2]); y=int(sys.argv[3])
L = [0,1,1]*j + [0,1,BLANK]
R = [1,1]+[1,1]*r + [0,1]+[1]*y+[0,BLANK]
cfg=('C',L,R,'>')
print(show(cfg))
n=0
while n<2000:
    try: head(cfg)
    except Stuck: break
    try: cfg=step(cfg)
    except Exception as e: print(e); break
    n+=1
    if cfg[0] in 'A' and cfg[3]=='>' and cfg[1]==[BLANK]: print(n,show(cfg)); break
print(n,show(cfg))
