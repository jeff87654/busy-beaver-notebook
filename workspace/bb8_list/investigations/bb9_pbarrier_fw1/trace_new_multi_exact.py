import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle
from trace_exact import run_trace

NEW_MULTI = "1RB0LB_1RC1RE_1LD1LF_1LB0LE_1LG0LC_0LD1RA_---0RF"
# Template: R,E,P=1,u=011,s=0,d=1d+0,b=1b+0,S=1 (SIDE=R -> mirror=False, Q='E' -> q=4)
def w_nm(ds, a, b):
    return '1' + ''.join('011'*x + '0' for x in list(ds) + [a]) + '011'*b + '1'

print("=== NEW_MULTI on D: [1, 2; 1; 1] -> [1, 1; 4; 1] ===")
w = w_nm([1, 2], 1, 1)
run_trace(NEW_MULTI, False, w, len(w), 'E', max_steps=200, print_every=0, stop_on_q=4)

print("\n=== NEW_MULTI on B2: [1, 0, 0; 4; 1] -> [0, 8, 1; 1; 1] ===")
w = w_nm([1, 0, 0], 4, 1)
run_trace(NEW_MULTI, False, w, len(w), 'E', max_steps=800, print_every=0, stop_on_q=4)

print("\n=== NEW_MULTI on E: [; 1; 1] -> [2, 0, 1^6; 1; 1] ===")
w = w_nm([], 1, 1)
run_trace(NEW_MULTI, False, w, len(w), 'E', max_steps=1300, print_every=1, stop_on_q=4)
