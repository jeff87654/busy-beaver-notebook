import sys, os
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\dl3_hits')
import idle
import kl
from egrid import short
from analyze_reb_E1_and_E2 import run_and_slots

base_tm = '1RB0LE_0LC0LD_0LD1LD_0RE1LC_1RA1RF_1RA0RG_---0RB'
print("=== D, B1, B2 with prefix digit [3, ...] on reb_E1 (F0=1RA) ===")
for label, ds, a in [
    ('D [3, 2; 4]', [3, 2], 4),
    ('B1 [3, 2, 0; 4]', [3, 2, 0], 4),
    ('B2 [3, 2, 0, 0; 4]', [3, 2, 0, 0], 4),
    ('E [0, 0; 4]', [0, 0], 4),
]:
    ev1, used = run_and_slots(base_tm, ds, a)
    print(f"  {label:20s} -> {ev1} | F0={'F0' in used} | used={used}")

print("\n=== Blank trace of the other 8 F0 variants of reb_E1 ===")
t_str = 'L,D,P=10,u=1,s=0,d=1d+1,b=1b+0,S=0'
for f0 in ['1RA', '0RC', '1RC', '0RD', '1RD', '0RE', '0RF', '1RF', '0RG']:
    tm = f"1RB0LE_0LC0LD_0LD1LD_0RE1LC_1RA1RF_{f0}0RG_---0RB"
    t = kl.tmpl(tm, t_str)
    evs = kl.blank(tm, 20000, maxl=40, T=t)
    k_evs = [f"{e[1]}:K({short(e[2])};{e[3]})" for e in evs if e[0] == 'K' and e[4] == 1]
    print(f"  F0={f0}: {k_evs[:6]} (total={len(evs)}, last={evs[-1]})")
