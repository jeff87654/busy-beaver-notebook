import sys, os
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl3_hits')
import idle
import kl
from egrid import short
from verify_rebE2_and_all_rules import trace_k_single

os.environ['PATH'] = r'C:\msys64\ucrt64\bin;C:\msys64\mingw64\bin;' + os.environ.get('PATH', '')

tm_rebE2 = "1RB0RG_1RC1RA_1RD1RC_0LE0LF_0LF1LF_0RB1LE_---0RC"
t_rebE2 = "L,F,P=-,u=1,s=0,d=1d+0,b=1b+0,S=0"

print("=== 1. reb_E2: Tracing inner odd digits and Round 2 exhaustion [1, 0^k, 1; a] ===")
for ds in [
    [3, 1], [3, 0, 1], [3, 0, 0, 1],
    [1, 1], [1, 0, 1], [1, 0, 0, 1], [1, 0, 0, 0, 1],
    [1, 3], [1, 0, 3], [1, 0, 1, 0], [1, 0, 0, 1, 0]
]:
    for a in [5, 7]:
        ev, used, hits = trace_k_single(tm_rebE2, t_rebE2, 1, ds, a)
        print(f"  K({short(ds):10s}; a={a}; 1) -> {ev} | A0 hits={len(hits)}")
        for st, ft in hits:
            print(f"      step {st}: {ft}")

print("\n=== 2. Full trajectory of synthetic small Round 1 -> Round 2 -> Round 3 on reb_E2 ===")
# Suppose we start at K(1, 0; a=3; 1) -> K(5, 2, 3, 0; 3; 1). Too large!
# What about K(1, 0; a=2; 1) or K(3, 1; a=1; 1)? Let's trace K(1, 0, 1; a=3; 1) for 20 K-steps!
T_E2 = kl.tmpl(tm_rebE2, t_rebE2)
evs = kl.run(tm_rebE2, [3, 0, 1], 1, 1, steps=200000, nchg=0, maxl=100, T=T_E2, pall=1)
for e in evs:
    if e[0] == 'K' and e[4] == 1:
        print(f"  step {e[1]:6d}: K({short(e[2])}; {e[3]}; {e[4]})")

print("\n=== 3. multi_1 and w1loop_1: What happens at K(0^k; a; 1)? ===")
tm_m1 = "1RB0LB_1RC1RE_1LD1LF_1LB0LE_1LG0LC_0LD1RA_---0RF"
t_m1 = "R,E,P=1,u=011,s=0,d=1d+0,b=1b+0,S=1"
T_m1 = kl.tmpl(tm_m1, t_m1)
for ds in [[1, 0], [0, 0], [0], []]:
    evs = kl.run(tm_m1, ds, 1, 1, steps=200000, nchg=0, maxl=30, T=T_m1, pall=1)
    k_b1 = [f"K({short(e[2])};{e[3]};{e[4]})@{e[1]}" for e in evs[1:] if e[0] == 'K' and e[4] == 1][:5]
    k_all = [f"K({short(e[2])};{e[3]};{e[4]})@{e[1]}" for e in evs[1:] if e[0] == 'K'][:6]
    print(f"  multi_1 K({short(ds):6s}; 1; 1): B=1 -> {k_b1} | all -> {k_all}")

tm_w1 = "1RB0RE_1RC1RA_0LD0LE_1RE0LE_0RF1LC_1LC1RG_0RB---"
t_w1 = "L,F,P=1,u=10,s=0,d=2d+0,b=2b+1,S=-"
T_w1 = kl.tmpl(tm_w1, t_w1)
for ds in [[1, 0], [0, 0], [0], []]:
    evs = kl.run(tm_w1, ds, 1, 1, steps=200000, nchg=0, maxl=30, T=T_w1, pall=1)
    k_b1 = [f"K({short(e[2])};{e[3]};{e[4]})@{e[1]}" for e in evs[1:] if e[0] == 'K' and e[4] == 1][:5]
    k_all = [f"K({short(e[2])};{e[3]};{e[4]})@{e[1]}" for e in evs[1:] if e[0] == 'K'][:6]
    print(f"  w1loop_1 K({short(ds):6s}; 1; 1): B=1 -> {k_b1} | all -> {k_all}")
