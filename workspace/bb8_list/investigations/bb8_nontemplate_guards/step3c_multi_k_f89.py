import os, sys

F89_CODE = "1RB0RE_0RC---_1LD0RG_1RA0RF_1LF0LD_1LD0LE_1RC1RE"
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

def run_multi_k(trans, L_init, max_steps=100000, max_k=30):
    tape, head, st = make_k_tape(L_init)
    min_vis = 0
    k_list = []
    for step in range(1, max_steps + 1):
        cur = tape.get(head, 0)
        tr = trans.get((st, cur))
        if tr is None:
            return ("HALT", step, f"{st}{cur}", k_list)
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
                k_list.append((step, L))
                if len(k_list) >= max_k:
                    return ("MAX_K", step, L, k_list)
    return ("TIMEOUT", max_steps, None, k_list)

base_trans = parse_tm(F89_CODE)

ALL_ACTIONS = [None]
for w in (0, 1):
    for d in (-1, 1):
        for s in STATES_8:
            ALL_ACTIONS.append((w, d, s))

print("=================================================================")
print("1. MULTI-K TRACE OF ALL GUARD-PAIR REDIRECTS ON {B0:0, C0:0, C0:1, G0:0}")
print("=================================================================")

guard_pairs = [("B", 0, 0), ("C", 0, 0), ("C", 0, 1), ("G", 0, 0)]
for st_x, sym_x, s_guard in guard_pairs:
    old_w, old_d, old_nxt = base_trans[(st_x, sym_x)]
    other_sym = 1 - s_guard
    old_other = base_trans[(old_nxt, other_sym)]
    print(f"\n--- Guard {st_x}{sym_x}:{s_guard} ---")
    for act in ALL_ACTIONS:
        t = dict(base_trans)
        t[(st_x, sym_x)] = (old_w, old_d, 'H')
        t[('H', other_sym)] = old_other
        t[('H', s_guard)] = act
        
        r1 = run_multi_k(t, [1], max_steps=50000, max_k=25)
        r3 = run_multi_k(t, [3], max_steps=50000, max_k=25)
        r5 = run_multi_k(t, [5], max_steps=50000, max_k=25)
        if r1[0] == "HALT" and len(r1[3]) == 0 and r3[0] == "HALT" and len(r3[3]) == 0:
            continue # Immediate E1 halt on all x
        if r1[0] == "TIMEOUT" and len(r1[3]) == 0 and r3[0] == "TIMEOUT" and len(r3[3]) == 0:
            continue # Immediate E1 runaway/loop on all x
        print(f"  act={act}:")
        for x, r in [(1, r1), (3, r3), (5, r5)]:
            ks_str = " -> ".join(f"{L}@{stp}" for stp, L in r[3][:6])
            if len(r[3]) > 6:
                ks_str += f" ... ({len(r[3])} K-events, last={r[3][-1][1]}@{r[3][-1][0]})"
            print(f"    x={x}: {r[0]} at {r[1]} ({r[2]}) | K: {ks_str}")
