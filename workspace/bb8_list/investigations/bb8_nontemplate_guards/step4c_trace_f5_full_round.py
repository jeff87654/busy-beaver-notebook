import os, sys
from step4_analyze_f5_redirects import F5_M1, F5_M2, F5_M3, parse_tm, build_m3_tape, parse_m3_k, run_m3_macro

STATES_8 = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
ALL_ACTIONS = [None]
for w in (0, 1):
    for d in (-1, 1):
        for s in STATES_8:
            ALL_ACTIONS.append((w, d, s))

def run_blank(trans, max_steps=40000):
    tape = {}
    head = 0
    st = 'A'
    for step in range(1, max_steps + 1):
        cur = tape.get(head, 0)
        tr = trans.get((st, cur))
        if tr is None:
            return ("HALT", step, f"{st}{cur}")
        w, d, nxt = tr
        if w == 0: tape.pop(head, None)
        else: tape[head] = 1
        head += d
        st = nxt
    return ("TIMEOUT", max_steps, None)

print("=================================================================")
print("1. SCREEN ALL 26*33 = 858 GUARD-PAIR REDIRECTS ON F5-M1, M2, M3")
print("=================================================================")

for name, code, halt_slot in [("F5-M1", F5_M1, "F1"), ("F5-M2", F5_M2, "F1"), ("F5-M3", F5_M3, "D1")]:
    base_trans = parse_tm(code)
    halts_over_300 = []
    max_halt = 0
    total_halts = 0
    for s_idx in range(7):
        st_x = chr(ord('A') + s_idx)
        for sym_x in (0, 1):
            slot = f"{st_x}{sym_x}"
            if slot == halt_slot:
                continue
            old_w, old_d, old_nxt = base_trans[(st_x, sym_x)]
            for s_guard in (0, 1):
                other_sym = 1 - s_guard
                old_other = base_trans.get((old_nxt, other_sym))
                for act in ALL_ACTIONS:
                    t = dict(base_trans)
                    t[(st_x, sym_x)] = (old_w, old_d, 'H')
                    t[('H', other_sym)] = old_other
                    t[('H', s_guard)] = act
                    r = run_blank(t, max_steps=25000)
                    if r[0] == "HALT":
                        total_halts += 1
                        if r[1] > max_halt:
                            max_halt = r[1]
                        if r[1] > 300:
                            halts_over_300.append((f"{slot}:{s_guard}", act, r[1], r[2]))
    print(f"\n[{name}] total_halts={total_halts}/858, max_halt={max_halt}, halts_>300={len(halts_over_300)}")
    for gp, act, stp, sl in sorted(halts_over_300, key=lambda x: -x[2])[:20]:
        print(f"  step={stp:5d} ({sl}) guard={gp} act={act}")
