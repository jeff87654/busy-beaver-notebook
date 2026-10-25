import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle
from backtrack_c4_9state import parse_tm, make_exhaustion_tape, check_valid_odd_k, run_fixed_tm

# Let's check why C1=1RH H0=0RB H1=0LD (and its state-I splits) wasn't in good_21 or what happened to it!
base_tr = parse_tm("1RB0RG_1RC1RB_0RD---_0LE0LD_0LF1LE_1RA1LF_0LD0RB")
# In C1=1RH H0=0RB H1=0LD:
tr = dict(base_tr)
tr[(2, 1)] = (1, 1, 7)   # C1 = 1RH
tr[(7, 0)] = (0, 1, 1)   # H0 = 0RB
tr[(7, 1)] = (0, -1, 3)  # H1 = 0LD

print("Testing C1=1RH H0=0RB H1=0LD with run_fixed_tm:")
for k in (3, 4, 5, 21):
    for M in (4, 5):
        print(f"  k={k:2d}, M={M}: {run_fixed_tm(tr, k=k, M=M, max_steps=15000)}")
