import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle
from verify_rule_d import parse_tm
from test_ackermann_macro import run_ackermann_sim

CANDIDATES = [
    ("1LG0LI_1LH--- (P=3: K*,K*,H*)", "1RB0RG_1RC1RB_0RD0LH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_1LG0LI_1LH---"),
    ("---0RI_1LI0LE (P=6: K*,H*,H*)", "1RB0RG_1RC1RB_0RD0RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_---0RI_1LI0LE"),
    ("---0LI_1LG0LH (P=5: K*x4, H*)", "1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_---0LI_1LG0LH"),
    ("---0RI_1RF1LG (P=2: H*,K*)",    "1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_---0RI_1RF1LG"),
    ("0LG0LI_1LH--- (P=5: K*x4, H*)", "1RB0RG_1RC1RB_0RD0RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_0LG0LI_1LH---"),
    ("---0LI_0RI0RG (P=6: H*,K*x5)",  "1RB0RG_1RC1RB_0RD0RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_---0LI_0RI0RG"),
]

for label, tm in CANDIDATES:
    print(f"=== {label}: {tm} ===")
    tr = parse_tm(tm)
    for k in range(1, 22):
        res = run_ackermann_sim(tr, k, 2*k + 6, is_232=False, max_iters=15000)
        print(f"  k={k:2d}: kind={res[0]:2s} dL/slot={str(res[2]):3s} I={res[3]} a={res[4]:3d} c={res[5]:2d} iters={res[6]}")
