import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle
from test_small_lists import run_from_config

for k in [1, 2, 3, 4]:
    cfg = "E[0]11111" + ("0011" * k) + "001"
    run_from_config(f"C4_1 (k={k})", "1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_0LD0RB", cfg, 2000000)
    run_from_config(f"C4_2 (k={k})", "1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_1LC0RB", cfg, 2000000)
