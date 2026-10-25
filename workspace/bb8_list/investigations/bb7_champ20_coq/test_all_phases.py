import sys, os
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb8_list\autoproof')
import planner8 as pl
from planner8 import BLANK, mkrun, V
import engine, validate

M1 = "1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_0LD0RB"
M2 = "1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_1LC0RB"

for mname, tm in [('M1', M1), ('M2', M2)]:
    pl.set_tm(tm)
    # After GLOOPS 19:
    L = [0, 1, 0, 1] * 19 + [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, BLANK]
    cfg = ('G', L, [BLANK], '>')
    want = ('E', [BLANK], [1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 0] + [1, 1, 0, 0] * 20 + [1, BLANK], '<')
    for st in range(1, 300):
        cfg = pl.step(cfg)
        if cfg[0] == 'E' and cfg[1] == [BLANK] and validate.same(cfg, want):
            print(f"{mname}: reached Kd (repeat 1 20) 1 2 in {st} steps after GLOOPS 19!")
            break
