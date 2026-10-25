import os, sys

F89_CODE = "1RB0RE_0RC---_1LD0RG_1RA0RF_1LF0LD_1LD0LE_1RC1RE"
STATES_7 = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
STATES_8 = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']

def parse_tm(code):
    parts = code.strip().split("_")
    trans = {}
    for s_idx, p in enumerate(parts):
        st = chr(ord('A') + s_idx)
        for sym in (0, 1):
            chunk = p[3*sym:3*sym+3]
            if chunk == "---":
                trans[(st, sym)] = None
            else:
                trans[(st, sym)] = (int(chunk[0]), -1 if chunk[1] == 'L' else 1, chunk[2])
    return trans

def make_k_tape(L):
    # [D]0 0 0 [1 (01)^d1] ... [1 (01)^dn]
    bits = [0, 0, 0]
    for d in L:
        bits.append(1)
        for _ in range(d):
            bits.extend([0, 1])
    tape = {i: b for i, b in enumerate(bits) if b != 0}
    return tape, 0, 'D'

def check_k_config(tape, head, state, min_vis):
    if state != 'D' or head != min_vis:
        return None
    mx = max(tape.keys()) if tape else head
    bits = [tape.get(i, 0) for i in range(head, mx + 1)]
    while bits and bits[-1] == 0:
        bits.pop()
    if len(bits) < 4 or bits[0] != 0 or bits[1] != 0 or bits[2] != 0 or bits[3] != 1:
        return None
    i = 3
    L = []
    while i < len(bits):
        if bits[i] != 1:
            return None
        i += 1
        d = 0
        while i + 1 < len(bits) and bits[i] == 0 and bits[i+1] == 1:
            d += 1
            i += 2
        L.append(d)
    return L

def run_from_k(trans, L_init, max_steps=15000):
    tape, head, st = make_k_tape(L_init)
    min_vis = 0
    for step in range(1, max_steps + 1):
        cur = tape.get(head, 0)
        tr = trans.get((st, cur))
        if tr is None:
            return ("HALT", step, f"{st}{cur}")
        w, d, nxt = tr
        if w == 0:
            tape.pop(head, None)
        else:
            tape[head] = 1
        head += d
        st = nxt
        if head < min_vis:
            min_vis = head
            L = check_k_config(tape, head, st, min_vis)
            if L is not None:
                return ("K", step, L)
    return ("TIMEOUT", max_steps, None)

base_trans = parse_tm(F89_CODE)

ALL_ACTIONS = [None]
for w in (0, 1):
    for d in (-1, 1):
        for s in STATES_8:
            ALL_ACTIONS.append((w, d, s))

print("=================================================================")
print("1. TEST ALL GUARD-PAIR REDIRECTS ON {B0:0, C0:0, C0:1, G0:0} ON S([x])")
print("=================================================================")

guard_pairs = [("B", 0, 0), ("C", 0, 0), ("C", 0, 1), ("G", 0, 0)]
for st_x, sym_x, s_guard in guard_pairs:
    old_w, old_d, old_nxt = base_trans[(st_x, sym_x)]
    other_sym = 1 - s_guard
    old_other = base_trans[(old_nxt, other_sym)]
    
    outcomes_summary = {}
    interesting = []
    for act in ALL_ACTIONS:
        t = dict(base_trans)
        t[(st_x, sym_x)] = (old_w, old_d, 'H')
        t[('H', other_sym)] = old_other
        t[('H', s_guard)] = act
        
        res_x = []
        for x in (1, 3, 5, 7, 9, 11):
            r = run_from_k(t, [x], max_steps=8000)
            res_x.append((x, r[0], r[1], r[2]))
        
        kinds = tuple(r[1] for r in res_x)
        outcomes_summary[kinds] = outcomes_summary.get(kinds, 0) + 1
        # Check if any K outcome differs from standard [1^(x+2)] or if kinds is mixed
        is_std = all(r[1] == "K" and r[3] == [1]*(r[0]+2) for r in res_x)
        if not is_std and any(r[1] == "K" for r in res_x) or len(set(kinds)) > 1:
            interesting.append((act, res_x))
    print(f"\nGuard {st_x}{sym_x}:{s_guard} (33 variants): summary={outcomes_summary}")
    for act, rx in interesting:
        print(f"  INTERESTING act={act}:")
        for x, knd, stp, val in rx:
            print(f"    x={x:2d}: {knd} at step {stp} -> {val}")
