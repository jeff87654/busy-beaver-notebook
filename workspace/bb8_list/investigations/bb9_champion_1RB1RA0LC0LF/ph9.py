import planner9 as pl
from planner9 import *
cfg=('A',[BLANK],[BLANK],'>')
for n in range(1,25):
    cfg=step(cfg)
    print(n,show(cfg))
