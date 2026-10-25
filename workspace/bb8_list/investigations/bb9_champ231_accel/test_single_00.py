import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle
from verify_rule_d import parse_tm
from test_jrem import run_from_e0_str

tm = "1RB0RG_1RC1RB_0RD0LH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_---1LI_1RB1LH"
tr = parse_tm(tm)

print("=== Testing [E0] 100 1^30 (00)^m 1 00 1^30 0000 (1100)^6 1 for m = 1..18 ===")
for m in range(1, 19):
    s_r = "100" + "1"*30 + "00"*m + "100" + "1"*30 + "0000" + "1100"*6 + "1"
    print(f"  m={m:2d} (j_rem={m+1:2d}, k={m+7:2d}): {run_from_e0_str(tr, s_r, 6)}")
