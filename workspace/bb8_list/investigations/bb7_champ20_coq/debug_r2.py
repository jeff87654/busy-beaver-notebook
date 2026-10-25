import sys, os
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb8_list\autoproof')
import planner8 as pl
from planner8 import BLANK, mkrun, V

M1 = "1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_0LD0RB"
pl.set_tm(M1)

s = ('E', [BLANK], pl.norm_side([1] + mkrun((1, 1), {'b': 1}, 0) + [0, 0, 0, 0, 1, 1] + mkrun((1, 1), {'y': 1}, 0) + [0, 0, V('t')]), '<')
cfg = s
for step_i in range(35):
    try:
        pl.head(cfg)
        cfg = pl.step(cfg)
        print(f"step {step_i}: {pl.show(cfg)}")
    except pl.Stuck:
        r, why = pl.try_crossing(cfg)
        if r:
            cfg, lname = r
            print(f"cross {lname}: {pl.show(cfg)}")
        else:
            a = pl.try_align(cfg)
            cfg, aname = a
            print(f"align {aname}: {pl.show(cfg)}")
