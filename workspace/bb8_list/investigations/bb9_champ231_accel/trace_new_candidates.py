import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle
from verify_rule_d import parse_tm
from test_collapse import run_accel_v3

# Let's test N-independence (N = 2k+6 vs N = 2k+10) on these candidates!
cands = [
    ("0LB1LI_0LG_231", "1RB0RG_1RC1RB_0RD0LH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_0LB1LI_0LG---", False),
    ("0LB1LI_0LG_232", "1RB0RG_1RC1RB_0RD0LH_0LE0LD_0LF1LE_1RA1LF_1LC0RB_0LB1LI_0LG---", True),
    ("---0RI_1RA1RG_231", "1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_---0RI_1RA1RG", False),
    ("---0LI_1RF1LC_231", "1RB0RG_1RC1RB_0RD0LH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_---0LI_1RF1LC", False),
    ("---1LI_1RB1LH_231", "1RB0RG_1RC1RB_0RD0LH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_---1LI_1RB1LH", False),
    ("1LI0RH_1LC_231", "1RB0RG_1RC1RB_0RD0LH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_1LI0RH_1LC---", False),
]

for name, tm, is_232 in cands:
    print(f"================ {name}: {tm} ================")
    tr = parse_tm(tm)
    for k in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 20]:
        N1 = 2 * k + 6
        N2 = 2 * k + 10
        r1 = run_accel_v3(tr, k, N1, is_232=is_232, max_iters=30000, allow_collapse=True)
        r2 = run_accel_v3(tr, k, N2, is_232=is_232, max_iters=30000, allow_collapse=True)
        # Check if r1 and r2 have the same step/iters or if they ate the whole N tower!
        indep = (r1[0] == r2[0] and r1[1] == r2[1] and r1[6] == r2[6])
        dL1 = (r1[2] - N1) if r1[0].startswith('K') else 0
        dL2 = (r2[2] - N2) if r2[0].startswith('K') else 0
        print(f"  k={k:2d}: N={N1:2d}->{r1[0]:2s}(dL={dL1:+3d},step={r1[1]:13d},it={r1[6]:5d}) | N={N2:2d}->{r2[0]:2s}(dL={dL2:+3d},step={r2[1]:13d},it={r2[6]:5d}) | N_indep={indep}")
