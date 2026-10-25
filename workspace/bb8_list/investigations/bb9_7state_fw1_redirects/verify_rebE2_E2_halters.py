import sys, os
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl3_hits')
import idle
import kl
from egrid import short

os.environ['PATH'] = r'C:\msys64\ucrt64\bin;C:\msys64\mingw64\bin;' + os.environ.get('PATH', '')

t_str = "L,F,P=-,u=1,s=0,d=1d+0,b=1b+0,S=0"
tm_base = "1RB0RG_1RC1RA_1RD1RC_0LE0LF_0LF1LF_0RB1LE_---0RC"
T = kl.tmpl(tm_base, t_str)

print("=== 1. Analyzing the 3 redir=E1 E2_HALT machines ===")
E1_E2_MACHINES = [
    ("E1_I1_0LB", "1RB0RG_1RC1RA_1RD1RC_0LE0LF_0LF1LH_0RB1LE_---0RC_0LI1LE_0RF0LB"),
    ("E1_I1_0LD", "1RB0RG_1RC1RA_1RD1RC_0LE0LF_0LF1LH_0RB1LE_---0RC_0LI1LE_0RF0LD"),
    ("E1_I1_0LE", "1RB0RG_1RC1RA_1RD1RC_0LE0LF_0LF1LH_0RB1LE_---0RC_0LI1LE_0RF0LE"),
]

for name, tm in E1_E2_MACHINES:
    print(f"\n--- {name}: {tm} ---")
    for k in [2, 3, 5]:
        for a in [5, 7, 9, 11]:
            ds = [1] + [0]*k
            evs = kl.run(tm, ds, a, 1, steps=50000, nchg=0, maxl=15, T=T, pall=1)
            out = []
            for e in evs[1:]:
                if e[0] == 'H':
                    out.append(f"HALT({e[2]}{e[3]})@{e[1]}")
                    break
                elif e[0] == 'K' and e[4] == 1 and e[2] != ds:
                    out.append(f"K({short(e[2])}; {e[3]}; {e[4]})@{e[1]}")
                    if len(out) >= 3:
                        break
            print(f"  E1 K(1,0^{k}; a={a:2d}; 1) -> {' -> '.join(out)}")

    # Now trace what happens when the rebuilt K-config from E1 is exhausted!
    # Notice what E1(1, 0^k; a; 1) rebuilds! Let's check for a=7, k=5:
    evs = kl.run(tm, [1, 0, 0, 0, 0, 0], 7, 1, steps=50000, nchg=0, maxl=5, T=T, pall=1)
    rebuilt = next((e for e in evs[1:] if e[0] == 'K' and e[4] == 1 and e[2] != [1,0,0,0,0,0]), None)
    print(f"  Rebuilt from K(1,0^5; 7; 1): {rebuilt}")

    # Test synthetic small multi-round trajectory starting from K(3, 2; 3; 1) or K(1, 0; 3; 1)!
    evs_syn = kl.run(tm, [1, 0], 3, 1, steps=5000000, nchg=0, maxl=80, T=T, pall=1)
    print("  Trajectory from K(1, 0; 3; 1):")
    for e in evs_syn:
        if e[0] == 'H' or (e[0] == 'K' and e[4] == 1):
            print(f"    {e}")

print("\n=== 2. Analyzing the 20 redir=A0 E2_HALT machines ===")
A0_E2_MACHINES = [
    "0LH0RG_1RC1RA_1RD1RC_0LE0LF_0LF1LF_0RB1LE_0LD0RC_0LI1LH_1LG---",
    "0LH0RG_1RC1RA_1RD1RC_0LE0LF_0LF1LF_0RB1LE_0LG0RC_1LI0LH_0LD---",
    "1LH0RG_1RC1RA_1RD1RC_0LE0LF_0LF1LF_0RB1LE_0RI0RC_0LB0LA_1RA---",
    "1LH0RG_1RC1RA_1RD1RC_0LE0LF_0LF1LF_0RB1LE_0RI0RC_0LB0LA_0RD---",
    "1LH0RG_1RC1RA_1RD1RC_0LE0LF_0LF1LF_0RB1LE_---0RC_0LI1LA_0LB0LA",
    "1LH0RG_1RC1RA_1RD1RC_0LE0LF_0LF1LF_0RB1LE_---0RC_0LI0LH_0LB1LD",
    "1LH0RG_1RC1RA_1RD1RC_0LE0LF_0LF1LF_0RB1LE_0LB0RC_0LI0LH_0LG---",
    "1LH0RG_1RC1RA_1RD1RC_0LE0LF_0LF1LF_0RB1LE_0LB0RC_0LI1LH_0LG---",
]
for tm in A0_E2_MACHINES:
    evs_b = kl.blank(tm, 200000, maxl=15, T=T)
    k_b = [f"K({short(e[2])};{e[3]})@{e[1]}" for e in evs_b if e[0] == 'K' and e[4] == 1][:4]
    h_b = [f"H({e[2]}{e[3]})@{e[1]}" for e in evs_b if e[0] == 'H']
    print(f"\n  {tm}")
    print(f"    blank: {k_b + h_b}")
    for ds in [[1, 0, 0], [1, 0, 0, 0, 0, 0], [0, 0, 0], [1, 0, 0, 1]]:
        evs = kl.run(tm, ds, 7, 1, steps=20000, nchg=0, maxl=10, T=T, pall=1)
        res = next((e for e in evs[1:] if e[0] == 'H' or (e[0] == 'K' and e[4] == 1 and e[2] != ds)), ('END',))
        print(f"    from K({short(ds):6s}; 7; 1) -> {res}")
