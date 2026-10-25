import os, sys

F5_M1 = "1RB1RG_0LC0LD_1RF0LD_0RE1LB_1LB0RF_0RA---_1RA1RD"
F5_M2 = "1RB1RE_1RC1RA_0LD0LE_1RF0LE_0RG1LC_0RB---_1LC0RF"
F5_M3 = "1RB0LD_0RC0RG_1LD0RG_0LE---_1LB1LF_1LE1LG_0LA1RB"

from step4_analyze_f5_redirects import parse_tm, build_m3_tape, parse_m3_k, run_m3_macro

t_m3 = parse_tm(F5_M3)

print("=================================================================")
print("1. CHECK D0:0 ACROSS ALL T0 (A, [0], c) RESIDUES IN F5-M3")
print("=================================================================")

for c in (-1, 0, 1, 2, 3, 4, 5, 6):
    for A in (6, 7, 8):
        res = run_m3_macro(t_m3, A, [0], c)
        has_d00 = "D0:0" in res[4]
        print(f"  T0(A={A}, L=[0], c={c:2d}) [(A+c)%3={(A+c)%3 if c>=0 else -1}]: {res[0]}@{res[1]:4d} -> {str(res[2]):28s} | D0:0={has_d00} | extra_vs_D={sorted(res[4] - {'A0:0', 'A1:0', 'B0:0', 'B0:1', 'B1:0', 'B1:1', 'C0:0', 'C1:0', 'C1:1', 'D0:1', 'E0:0', 'E0:1', 'E1:0', 'E1:1', 'F0:0', 'F0:1', 'F1:0', 'G0:0', 'G0:1', 'G1:0', 'G1:1'})}")

print("\n=================================================================")
print("2. CHECK WHEN D0:0 (M3) / F0:0 (M1, M2) FIRES IN NATURAL RUNS")
print("=================================================================")

for name, code, guard_pair in [("F5-M1", F5_M1, "F0:0"), ("F5-M2", F5_M2, "F0:0"), ("F5-M3", F5_M3, "D0:0")]:
    trans = parse_tm(code)
    tape = {}
    head = 0
    st = 'A'
    g_steps = []
    all_pair_counts = {}
    for step in range(1, 30000):
        cur = tape.get(head, 0)
        slot = f"{st}{cur}"
        w, d, nxt = trans[(st, cur)]
        if w == 0: tape.pop(head, None)
        else: tape[head] = 1
        head += d
        st = nxt
        nxt_sym = tape.get(head, 0)
        pair = f"{slot}:{nxt_sym}"
        all_pair_counts[pair] = all_pair_counts.get(pair, 0) + 1
        if pair == guard_pair:
            g_steps.append(step)
    print(f"\n[{name}] {code}")
    print(f"  {guard_pair} count in 30,000 steps: {len(g_steps)} -> steps={g_steps}")
    rare = {k: v for k, v in sorted(all_pair_counts.items()) if v <= 10}
    print(f"  All pairs with count <= 10 in 30,000 steps: {rare}")
