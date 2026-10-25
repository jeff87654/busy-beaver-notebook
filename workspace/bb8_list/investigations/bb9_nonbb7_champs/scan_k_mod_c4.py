import sys, re
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle
from test_c4_8state_general_k_M import find_first_clean_k_or_halt

if __name__ == '__main__':
    for bname, g0 in [("C4_1", "0LD0RB"), ("C4_2", "1LC0RB")]:
        tm_str = f"1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_{g0}_---1RC"
        print(f"=== {bname} C1=1RH H0=--- H1=1RC (M=5) ===")
        for k in range(2, 35):
            res = find_first_clean_k_or_halt(tm_str, k, M=5, max_steps=60000)
            print(f"  k={k:2d}: {res}")
