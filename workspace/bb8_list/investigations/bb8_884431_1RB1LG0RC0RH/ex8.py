import sys
import planner8 as pl
from planner8 import *
pl.set_tm('1RB1LG_0RC0RH_1RD0RE_1LE---_1RF1RE_0LA0LG_1LH1LA_0RA0LA')
from ex7 import cfgK
ds=tuple(int(x) for x in sys.argv[1].split(',') if x); a=int(sys.argv[2]); bp=int(sys.argv[3]); lo=int(sys.argv[4]); hi=int(sys.argv[5])
cfg=cfgK(ds,a,bp)
for n in range(hi):
    if n>=lo: print(n,show(cfg))
    cfg=step(cfg)
