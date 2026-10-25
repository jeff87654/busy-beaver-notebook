import os, sys
os.environ["PATH"] = r"C:\msys64\ucrt64\bin;" + os.environ.get("PATH", "")
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl3_hits')
import kl

NEW_MULTI = "1RB0LB_1RC1RE_1LD1LF_1LB0LE_1LG0LC_0LD1RA_---0RF"
t_str = "R,E,P=1,u=011,s=0,d=1d+0,b=1b+0,S=1"
T = kl.tmpl(NEW_MULTI, t_str)

print("=== Testing NEW_MULTI on K(ds; a; 1) ===")
for ds, a in [
    ([1], 2),
    ([1, 2], 1),
    ([1, 0], 3),
    ([1, 0, 0], 4),
    ([1, 0, 0, 0], 5),
    ([], 1),
    ([], 2),
    ([], 3),
    ([], 4),
    ([], 5),
    ([2, 0], 1),
    ([2, 0], 2),
    ([2, 0], 3),
    ([2, 0], 4),
]:
    ev = kl.run(NEW_MULTI, ds, a, 1, steps=200000, nchg=3, maxl=10, T=T, pall=0)
    print(f"Start K({ds}; {a}; 1):")
    for e in ev[:8]:
        print("  ", e)
