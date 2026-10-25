import os
from step1_profile_transitions import parse_tm, trace_transitions, f89_tape, f89_is_p1

F89_ALL = [
    ("F89",    "1RB0RE_0RC---_1LD0RG_1RA0RF_1LF0LD_1LD0LE_1RC1RE", 4679),
    ("F89-S1", "1RB0LG_1LC0LE_1LF0LD_1RE0RB_1RB0RD_0LA---_1LA1LD", 162),
    ("F89-S2", "1RB0RD_1LC0LA_1LE0LD_1RA0RB_0LF---_1RB0LG_1LF1LD", 162),
    ("F89-S3", "1RB0RF_1RC0RE_0RD---_1LA0RG_1LF0LA_1LA0LE_1RD1RE", 13),
]

print("=== F89 & Siblings Prelude vs Post-Prelude Usage ===")
for name, m, pre_step in F89_ALL:
    T = parse_tm(m)
    tape = {}
    p = 0
    q = 0
    lo = hi = 0
    slot_steps = {}
    pair_steps = {}
    for st in range(1, 50000):
        s = tape.get(p, 0)
        slot = f"{chr(65+q)}{s}"
        tr = T[(q, s)]
        if tr is None:
            print(f"{name} HALT at {st}")
            break
        w, d, nq, _ = tr
        tape[p] = w
        p += d
        q = nq
        ns = tape.get(p, 0)
        pair = f"{slot}:{ns}"
        slot_steps.setdefault(slot, []).append(st)
        pair_steps.setdefault(pair, []).append(st)
    print(f"\n[{name}] {m} (odd template starts at step {pre_step})")
    for sl, sts in sorted(slot_steps.items()):
        after = [x for x in sts if x > pre_step]
        if len(after) < 10:
            print(f"  Slot {sl}: total={len(sts)}, <=pre={len([x for x in sts if x <= pre_step])}, >pre={after[:10]}")
    for pr, sts in sorted(pair_steps.items()):
        after = [x for x in sts if x > pre_step]
        if len(after) < 10:
            print(f"  Pair {pr}: total={len(sts)}, <=pre={len([x for x in sts if x <= pre_step])}, >pre={after[:10]}")
