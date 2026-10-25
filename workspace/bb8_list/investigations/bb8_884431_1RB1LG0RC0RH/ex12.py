import sys
import planner8 as pl
from planner8 import *
pl.set_tm('1RB1LG_0RC0RH_1RD0RE_1LE---_1RF1RE_0LA0LG_1LH1LA_0RA0LA')
j=int(sys.argv[1]); r=int(sys.argv[2]); y=int(sys.argv[3]); nsteps=int(sys.argv[4])
cfg=('A',[0,1,1]*j+[0,1,1,0,1,BLANK],[1,1,1]+[1,1]*r+[0]+[1]*y+[0,BLANK],'>')
for n in range(nsteps):
    q,L,R,m=cfg
    if q=='A' and m=='<' and L==[BLANK]: print(n,show(cfg))
    elif q in 'C' and m=='>' : print(n,show(cfg))
    try: cfg=step(cfg)
    except Exception as e: print(e);break
