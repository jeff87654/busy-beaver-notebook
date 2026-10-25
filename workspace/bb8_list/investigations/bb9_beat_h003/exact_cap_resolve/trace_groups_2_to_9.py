import sys
from inspect_post_m5_2 import run_inspect

print("=== GROUP 2: 1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_---1RI_1RA0RE ===")
for k in [5, 6, 7, 8, 9, 10, 11, 14, 17, 20]:
    run_inspect("1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_---1RI_1RA0RE", k, 2*k+10, CAPX=0)

print("\n=== GROUP 3/4: 1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_---1RI_0LE0LF ===")
for k in [2, 3, 5, 6, 7, 8, 14, 20]:
    run_inspect("1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_---1RI_0LE0LF", k, 2*k+10, CAPX=0)
