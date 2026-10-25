import sys, os
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl3_hits')
import idle
import kl
from egrid import short

os.environ['PATH'] = r'C:\msys64\ucrt64\bin;C:\msys64\mingw64\bin;' + os.environ.get('PATH', '')

tm_base = "1RB0RG_1RC1RA_1RD1RC_0LE0LF_0LF1LF_0RB1LE_---0RC"
tm_9 = "1RB0RG_1RC1RA_1RD1RC_0LE0LF_0LF1LH_0RB1LE_0RB0RC_0LI1LE_0RG---"
t_str = "L,F,P=-,u=1,s=0,d=1d+0,b=1b+0,S=0"
T = kl.tmpl(tm_base, t_str)

print("=== 1. Blank-tape trajectory of 9-state machine tm_9 ===")
evs_blank = kl.blank(tm_9, 2000000, maxl=30, T=T)
for e in evs_blank:
    if e[0] == 'K':
        print(f"  step {e[1]:8d}: K({short(e[2])}; {e[3]}; {e[4]})")
    else:
        print(f"  {e}")

print("\n=== 2. Testing D and B_k on tm_9 vs tm_base ===")
test_cases = [
    ("D even [5, 4; 3]", [5, 4], 3),
    ("D even [5, 2; 9]", [5, 2], 9),
    ("B1 [5, 4, 0; 3]", [5, 4, 0], 3),
    ("B2 [5, 4, 0, 0; 3]", [5, 4, 0, 0], 3),
    ("B3 [5, 4, 0, 0, 0; 3]", [5, 4, 0, 0, 0], 3),
    ("B5 [5, 0^5; 3]", [5, 0, 0, 0, 0, 0], 3),
    ("B5 [3, 0^5; 3]", [3, 0, 0, 0, 0, 0], 3),
    ("E1 [1, 0^5; 3]", [1, 0, 0, 0, 0, 0], 3),
    ("E1 [1, 0^5; 7]", [1, 0, 0, 0, 0, 0], 7),
    ("E1 [1, 0^5; 9]", [1, 0, 0, 0, 0, 0], 9),
    ("E1 [1, 0^2; 5]", [1, 0, 0], 5),
    ("E1 [1, 0; 5]", [1, 0], 5),
    ("E1 [1; 5]", [1], 5),
]

for label, ds, a in test_cases:
    ev_b = kl.run(tm_base, ds, a, 1, steps=100000, nchg=0, maxl=20, T=T, pall=1)
    ev_9 = kl.run(tm_9, ds, a, 1, steps=100000, nchg=0, maxl=20, T=T, pall=1)
    b_res = next((e for e in ev_b[1:] if e[0] == 'H' or (e[0] == 'K' and e[4] == 1 and e[2] != ds)), ('END',))
    r_res = next((e for e in ev_9[1:] if e[0] == 'H' or (e[0] == 'K' and e[4] == 1 and e[2] != ds)), ('END',))
    print(f"  {label:22s} | base: {b_res} | 9-state: {r_res}")

print("\n=== 3. Full blank-tape simulation of synthetic smaller tower K(3, 2; 3; 1) on tm_9 ===")
evs_syn = kl.run(tm_9, [3, 2], 3, 1, steps=5000000, nchg=0, maxl=200, T=T, pall=1)
for e in evs_syn:
    if e[0] == 'H' or (e[0] == 'K' and e[4] == 1):
        print(f"  {e}")
