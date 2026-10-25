import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle
from test_small_lists import run_from_config

print("=== Testing C4_1 and C4_2 at k=20 from K(0^20; a=0; b=B) = E[0] 1^B (00)^20 001 ===")
for B in [39, 41, 43, 45, 47, 49, 51, 99]:
    cfg = "E[0]" + ("1" * B) + ("00" * 20) + "001"
    run_from_config(f"C4_1 k=20 B={B}", "1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_0LD0RB", cfg, 200000)
    run_from_config(f"C4_2 k=20 B={B}", "1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_1LC0RB", cfg, 200000)
