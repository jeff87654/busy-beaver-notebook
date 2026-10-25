import planner8 as pl
from planner8 import *
pl.set_tm('1RB1LG_0RC0RH_1RD0RE_1LE---_1RF1RE_0LA0LG_1LH1LA_0RA0LA')
cfg=('A',[0,1,1,0,1,BLANK],[1,1,1]+mkrun((1,1),{'r':1})+[0,V('w')],'>')
for n in range(8):
    print(n,show(cfg))
    cfg=step(cfg)
