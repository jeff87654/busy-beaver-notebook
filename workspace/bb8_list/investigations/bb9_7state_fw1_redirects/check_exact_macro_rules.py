import sys, os
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl3_hits')
import idle
import kl
from egrid import short

os.environ['PATH'] = r'C:\msys64\ucrt64\bin;C:\msys64\mingw64\bin;' + os.environ.get('PATH', '')

def test_configs(name, tm, t_str, B0, configs, maxs=500000):
    t = kl.tmpl(tm, t_str)
    print(f"\n=== {name}: {tm} ({t_str}, B={B0}) ===")
    for label, ds, a in configs:
        evs = kl.run(tm, ds, a, B0, steps=maxs, nchg=0, maxl=50000, T=t, pall=1)
        out = []
        for e in evs[1:]:
            if e[0] == 'H':
                out.append(f"HALT@{e[1]}({e[2]}{e[3]})")
                break
            elif e[0] == 'K' and e[4] == B0:
                out.append(f"K({short(e[2])}; {e[3]}; {e[4]})@{e[1]}")
                if len(out) >= 4:
                    break
        print(f"  {label:20s} K({short(ds)}; {a}; {B0}) -> " + " -> ".join(out))

# 1. reb_E2 in 1d+0 coding
test_configs("reb_E2 (1d+0)", "1RB0RG_1RC1RA_1RD1RC_0LE0LF_0LF1LF_0RB1LE_---0RC", "L,F,P=-,u=1,s=0,d=1d+0,b=1b+0,S=0", 1, [
    ("D even", [5, 4], 3),
    ("D odd", [5, 3], 3),
    ("B1 from even", [5, 4, 0], 3),
    ("B2 from even", [5, 4, 0, 0], 3),
    ("B1 from 5", [5, 0], 3),
    ("B2 from 5", [5, 0, 0], 3),
    ("B2 from 3", [3, 0, 0], 3),
    ("E from [1, 0, 0] a=3", [1, 0, 0], 3),
    ("E from [1, 0, 0] a=5", [1, 0, 0], 5),
    ("E from [1, 0, 0, 0] a=3", [1, 0, 0, 0], 3),
    ("E from [0, 0] a=3", [0, 0], 3),
    ("E from [0, 0] a=5", [0, 0], 5),
    ("E from [] a=3", [], 3),
    ("E from [] a=6", [], 6),
])

# 2. reb_E1_1 in 1d+0 coding
test_configs("reb_E1_1 (1d+0)", "1RB0LE_0LC0LD_0LD1LD_0RE1LC_1RA1RF_1RA0RG_---0RB", "L,D,P=-,u=1,s=0,d=1d+0,b=1b+0,S=0", 1, [
    ("D even", [1, 4], 3),
    ("B1 from even", [1, 4, 0], 3),
    ("B2 from even", [1, 4, 0, 0], 3),
    ("B1 from 3", [1, 3, 0], 3),
    ("B2 from 3", [1, 3, 0, 0], 3),
    ("from [1, 1, 0, 0] a=3", [1, 1, 0, 0], 3),
    ("from [1, 0, 0] a=3", [1, 0, 0], 3),
    ("from [1, 0, 0] a=5", [1, 0, 0], 5),
    ("from [0, 0] a=3", [0, 0], 3),
    ("from [] a=3", [], 3),
])

# 3. multi_1 in 1d+0 coding
test_configs("multi_1 (1d+0)", "1RB0LB_1RC1RE_1LD1LF_1LB0LE_1LG0LC_0LD1RA_---0RF", "R,E,P=1,u=011,s=0,d=1d+0,b=1b+0,S=1", 1, [
    ("D", [2, 2], 1),
    ("B1", [2, 2, 0], 4),
    ("B2", [2, 2, 0, 0], 4),
    ("E [0,0] a=1", [0, 0], 1),
    ("E [0,0] a=4", [0, 0], 4),
    ("E [0,0,0] a=4", [0, 0, 0], 4),
    ("E [] a=1", [], 1),
    ("E [] a=4", [], 4),
])

# 4. w1loop_1 in 2d+0 coding
test_configs("w1loop_1 (2d+0)", "1RB0RE_1RC1RA_0LD0LE_1RE0LE_0RF1LC_1LC1RG_0RB---", "L,F,P=1,u=10,s=0,d=2d+0,b=2b+1,S=-", 1, [
    ("D", [1, 2], 1),
    ("B1", [1, 2, 0], 4),
    ("B2", [1, 2, 0, 0], 4),
    ("E [0,0] a=1", [0, 0], 1),
    ("E [0,0] a=4", [0, 0], 4),
    ("E [0,0,0] a=4", [0, 0, 0], 4),
    ("E [] a=1", [], 1),
    ("E [] a=4", [], 4),
])
