import sys, os
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb8_list\autoproof')
import planner8 as pl
from planner8 import BLANK, mkrun, V
import engine, validate

M1 = "1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_0LD0RB"
M2 = "1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_1LC0RB"

def K_cfg(b_cnt, b_c, a_cnt, a_c, rest):
    # 0^inf <E 1 (11)^b 00 (11)^a 00 rest
    R = [1] + mkrun((1, 1), b_cnt, b_c) + [0, 0] + mkrun((1, 1), a_cnt, a_c) + [0, 0] + rest
    return ('E', [BLANK], pl.norm_side(R), '<')

for name, tm in [('M1', M1), ('M2', M2)]:
    pl.set_tm(tm)
    print(f"=== {name} ===")
    # Test R1: K(W, a+1, b) -> K(W, a, b+3)
    s_r1 = K_cfg({'b': 1}, 0, {'a': 1}, 1, [V('r')])
    t_r1 = K_cfg({'b': 1}, 3, {'a': 1}, 0, [V('r')])
    tree = engine.explore(s_r1, t_r1)
    print("R1:", "\n  ".join(engine.describe(tree)))

    # Test R2: K(S y :: t, 0, b) -> K(y :: t, b+3, 0)
    s_r2 = K_cfg({'b': 1}, 0, {}, 0, [1, 1] + mkrun((1, 1), {'y': 1}, 0) + [0, 0, V('t')])
    t_r2 = K_cfg({}, 0, {'b': 1}, 3, mkrun((1, 1), {'y': 1}, 0) + [0, 0, V('t')])
    tree = engine.explore(s_r2, t_r2)
    print("R2:", "\n  ".join(engine.describe(tree)))

    # Test R3 for m zeros (k = m+1 >= 1), b = m + s:
    # K(0^(m+1) ++ S y :: t, 0, m + s) -> K(1^m ++ (s+2) :: y :: t, 1, 0)
    s_r3 = K_cfg({'m': 1, 's': 1}, 0, {}, 0, mkrun((0, 0), {'m': 1}, 1) + [1, 1] + mkrun((1, 1), {'y': 1}, 0) + [0, 0, V('t')])
    t_r3 = K_cfg({}, 0, {}, 1, mkrun((1, 1, 0, 0), {'m': 1}, 0) + mkrun((1, 1), {'s': 1}, 2) + [0, 0] + mkrun((1, 1), {'y': 1}, 0) + [0, 0, V('t')])
    try:
        tree = engine.explore(s_r3, t_r3)
        print("R3:", "\n  ".join(engine.describe(tree)))
    except Exception as e:
        print("R3 direct explore:", e)
