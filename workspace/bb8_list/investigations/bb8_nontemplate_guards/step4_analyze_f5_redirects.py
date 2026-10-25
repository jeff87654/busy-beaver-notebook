import os, sys

F5_M1 = "1RB1RG_0LC0LD_1RF0LD_0RE1LB_1LB0RF_0RA---_1RA1RD"
F5_M2 = "1RB1RE_1RC1RA_0LD0LE_1RF0LE_0RG1LC_0RB---_1LC0RF"
F5_M3 = "1RB0LD_0RC0RG_1LD0RG_0LE---_1LB1LF_1LE1LG_0LA1RB"

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

def build_m3_tape(A, L, c):
    content = [1, 0] * A + [0]
    for d in L[:-1]:
        content += [1, 0] * d + [0]
    e = L[-1]
    content += [1, 0] * e + [1]
    if c != -1:
        content += [1, 0] * c + [1]
    rev_c = list(reversed(content)) + [0, 0]
    head = len(rev_c)
    tape = {i: b for i, b in enumerate(rev_c) if b != 0}
    return tape, head, 'G'

def parse_m3_k(tape, head, state, max_vis):
    if state != 'G' or head != max_vis:
        return None
    if tape.get(head - 1, 0) != 0 or tape.get(head - 2, 0) != 0 or tape.get(head - 3, 0) != 1:
        return None
    mn = min(tape.keys()) if tape else head
    bits = [tape.get(i, 0) for i in range(mn, head - 2)]
    while bits and bits[0] == 0:
        bits.pop(0)
    content = list(reversed(bits))
    # Tokenize maximal (1, 0) runs as int, leftover 0 as '.', leftover 1 as '#'
    toks = []
    i = 0
    n_len = len(content)
    while i < n_len:
        run = 0
        while i + 1 < n_len and content[i] == 1 and content[i+1] == 0:
            run += 1
            i += 2
        if run > 0:
            toks.append(run)
        else:
            toks.append('.' if content[i] == 0 else '#')
            i += 1
    if len(toks) < 3 or not isinstance(toks[0], int) or toks[1] != '.':
        return None
    A = toks[0]
    idx = 2
    L = []
    while True:
        v = 0
        if idx < len(toks) and isinstance(toks[idx], int):
            v = toks[idx]
            idx += 1
        if idx >= len(toks):
            return None
        sep = toks[idx]
        idx += 1
        L.append(v)
        if sep == '#':
            break
        if sep != '.':
            return None
    c = -1
    if idx < len(toks):
        v = 0
        if isinstance(toks[idx], int):
            v = toks[idx]
            idx += 1
        if idx != len(toks) - 1 or toks[idx] != '#':
            return None
        c = v
    return (A, L, c)

def run_m3_macro(trans, A, L, c, max_steps=100000):
    tape, head, st = build_m3_tape(A, L, c)
    max_vis = head
    slots = set()
    pairs = set()
    for step in range(1, max_steps + 1):
        cur = tape.get(head, 0)
        slot = f"{st}{cur}"
        slots.add(slot)
        tr = trans.get((st, cur))
        if tr is None:
            return ("HALT", step, slot, slots, pairs)
        w, d, nxt = tr
        if w == 0: tape.pop(head, None)
        else: tape[head] = 1
        head += d
        st = nxt
        nxt_sym = tape.get(head, 0)
        pairs.add(f"{slot}:{nxt_sym}")
        if head > max_vis:
            max_vis = head
            cfg = parse_m3_k(tape, head, st, max_vis)
            if cfg is not None:
                return ("K", step, cfg, slots, pairs)
    return ("TIMEOUT", max_steps, None, slots, pairs)

print("=================================================================")
print("1. F5-M3 EXACT MACRO-STEP TRANSITION & GUARD-PAIR PROFILE")
print("=================================================================")

t_m3 = parse_tm(F5_M3)

test_configs = [
    ("D_ord_c-1",    8, [4, 2, 0], -1),
    ("D_ord_c3",     8, [4, 2, 1],  3),
    ("B1_ord_e0",    8, [0, 4, 0], -1),
    ("B1_ord_e1",    8, [0, 4, 1],  3),
    ("B2_ord_e0",    8, [0, 0, 4, 0], -1),
    ("B2_ord_e1",    8, [0, 0, 4, 1],  3),
    ("B1_att_e4",    8, [0, 4],    -1),
    ("B2_att_e4",    8, [0, 0, 4],  3),
    ("T1_e0",        8, [0, 0],    -1),
    ("T1_e1",        8, [0, 1],    -1),
    ("T2_e0",        8, [0, 0, 0], -1),
    ("T2_e1",        8, [0, 0, 1], -1),
    ("M1_e0",        8, [0, 0],     4),
    ("M1_e1",        8, [0, 1],     4),
    ("M2_e0",        8, [0, 0, 0],  4),
    ("M2_e1",        8, [0, 0, 1],  4),
    ("T0_no_c_e0",   8, [0],       -1),
    ("T0_no_c_e1",   8, [1],       -1),
    ("T0_with_c_e0", 8, [0],        4),
    ("T0_with_c_e1", 8, [1],        4),
]

ord_slots, ord_pairs = set(), set()
eng_slots, eng_pairs = set(), set()
exh_slots, exh_pairs = set(), set()

for name, A, L, c in test_configs:
    res = run_m3_macro(t_m3, A, L, c)
    if name.startswith("D_") or "_ord_" in name:
        ord_slots |= res[3]
        ord_pairs |= res[4]
        eng_slots |= res[3]
        eng_pairs |= res[4]
    elif "_att_" in name:
        eng_slots |= res[3]
        eng_pairs |= res[4]
    else:
        exh_slots |= res[3]
        exh_pairs |= res[4]

print(f"Pure Ordinary (D, Bj_ord) slots ({len(ord_slots)}): {sorted(ord_slots)}")
print(f"Pure Ordinary (D, Bj_ord) pairs ({len(ord_pairs)}): {sorted(ord_pairs)}")
print(f"Full Engine (D, Bj_ord, Bj_att) slots ({len(eng_slots)}): {sorted(eng_slots)}")
print(f"Full Engine (D, Bj_ord, Bj_att) pairs ({len(eng_pairs)}): {sorted(eng_pairs)}")
print(f"Exhaustion (Tk, Mj, T0) slots ({len(exh_slots)}): {sorted(exh_slots)}")
print(f"Exhaustion (Tk, Mj, T0) pairs ({len(exh_pairs)}): {sorted(exh_pairs)}")
print(f"Slots in Attached/Exhaustion but NOT Pure Ordinary: {sorted((eng_slots | exh_slots) - ord_slots)}")
print(f"Slots in Exhaustion (Tk, Mj, T0) but NOT Engine (D, Bj): {sorted(exh_slots - eng_slots)}")
print(f"Pairs in Attached/Exhaustion but NOT Pure Ordinary: {sorted((eng_pairs | exh_pairs) - ord_pairs)}")
print(f"Pairs in Exhaustion (Tk, Mj, T0) but NOT Engine (D, Bj): {sorted(exh_pairs - eng_pairs)}")

for name, A, L, c in test_configs:
    res = run_m3_macro(t_m3, A, L, c)
    print(f"  {name:14s}: {res[0]}@{res[1]:5d} -> {str(res[2]):26s} | vs_ord_slots={sorted(res[3]-ord_slots)} | vs_ord_pairs={sorted(res[4]-ord_pairs)} | vs_eng_pairs={sorted(res[4]-eng_pairs)}")
