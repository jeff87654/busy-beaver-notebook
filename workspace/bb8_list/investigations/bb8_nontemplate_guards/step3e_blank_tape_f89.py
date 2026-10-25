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

def run_blank(trans, start_st='A', max_steps=10000, max_k=15):
    tape = {}
    head = 0
    st = start_st
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
print("1. BLANK-TAPE SCREEN OF ALL 132 S-GUARD REDIRECTS (STARTS A, C, F, D)")
print("=================================================================")

guard_pairs = [("B", 0, 0), ("C", 0, 0), ("C", 0, 1), ("G", 0, 0)]
for start_label, start_st in [("F89(A)", 'A'), ("F89-S1(C)", 'C'), ("F89-S2(F)", 'F'), ("F89-S3(D)", 'D')]:
    print(f"\n=== Start {start_label} ===")
    for st_x, sym_x, s_guard in guard_pairs:
        old_w, old_d, old_nxt = base_trans[(st_x, sym_x)]
        other_sym = 1 - s_guard
        old_other = base_trans[(old_nxt, other_sym)]
        halts_with_k = []
        max_halt_no_k = 0
        k_survivors = 0
        for act in ALL_ACTIONS:
            t = dict(base_trans)
            t[(st_x, sym_x)] = (old_w, old_d, 'H')
            t[('H', other_sym)] = old_other
            t[('H', s_guard)] = act
            r = run_blank(t, start_st=start_st, max_steps=20000, max_k=25)
            if r[0] == "HALT":
                if len(r[3]) > 0 or r[1] > 200:
                    halts_with_k.append((act, r[1], r[2], r[3]))
                else:
                    if r[1] > max_halt_no_k:
                        max_halt_no_k = r[1]
            elif len(r[3]) > 0:
                k_survivors += 1
        print(f"  Guard {st_x}{sym_x}:{s_guard}: k_survivors={k_survivors}, max_early_halt={max_halt_no_k}, halts_with_k_or_>200={len(halts_with_k)}")
        for act, stp, sl, ks in halts_with_k:
            print(f"    HALT act={act}: step={stp} ({sl}) K_count={len(ks)} Ks={[L for _,L in ks[:6]]}")
