import sys, os
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb8_list\autoproof')
import planner8 as pl
from planner8 import BLANK, mkrun, V
import engine, validate

M1 = "1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_0LD0RB"
M2 = "1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_1LC0RB"

for name, tm in [('M1', M1), ('M2', M2)]:
    pl.set_tm(tm)
    print(f"=== {name} ===")
    # 1. Test GLOOP: (0 >> X) G> (1 >> 1 >> [1;1]^s *> const 0) -> (0 >> 1 >> 0 >> 1 >> 0 >> X) G> ([1;1]^s *> const 0)
    s_g = ('G', [0, V('X')], pl.norm_side([1, 1] + mkrun((1, 1), {'s': 1}, 0) + [BLANK]), '>')
    t_g = ('G', [0, 1, 0, 1, 0, V('X')], pl.norm_side(mkrun((1, 1), {'s': 1}, 0) + [BLANK]), '>')
    tree_g = engine.explore(s_g, t_g)
    print("GLOOP:", "\n  ".join(engine.describe(tree_g)))

    # 2. Test GHALT from ([0;1;0;1]^s *> 0 >> 1 >> 0 >> 1 >> 0 >> 1 >> 0 >> 1 >> 0 >> 1 >> 0 >> 1 >> 1 >> 0 >> [1;0;1;0]^m *> const 0) G> const 0:
    L_gh = mkrun((0, 1, 0, 1), {'s': 1}, 0) + [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0] + mkrun((1, 0, 1, 0), {'m': 1}, 0) + [BLANK]
    c_gh = ('G', pl.norm_side(L_gh), [BLANK], '>')
    ops_gh, c_gh_end, how_gh = engine.run_until_stuck(c_gh, None)
    print("GHALT:", how_gh, pl.show(c_gh_end))
    print("  raw:", c_gh_end)
    print("  ops:", ops_gh)
