import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle
from test_small_lists import run_from_config

print("=== Testing C4_1 and C4_2 directly from K(0^k; a=0; b=B) = E[0] 1^B (00)^k 001 ===")
for k in [1, 2, 3, 4, 5]:
    for B in [5, 7, 11, 13, 17, 19, 23, 25, 49]:
        cfg = "E[0]" + ("1" * B) + ("00" * k) + "001"
        status, steps, ones, final_tape = run_from_config(f"C4_1 k={k} B={B}", "1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_0LD0RB", cfg, 200000)
