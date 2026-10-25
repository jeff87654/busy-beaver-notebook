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

def run_from_k(trans, L_init, max_steps=6000, max_k=1):
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

def run_blank(trans, start_st='A', max_steps=8000):
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
                # If we hit an all-odd list of length >= 3, stop early and record it!
                if len(L) >= 3 and all(x % 2 == 1 for x in L):
                    return ("ODD_TOWER", step, L, k_list)
    return ("TIMEOUT", max_steps, None, k_list)

base_trans = parse_tm(F89_CODE)

ALL_ACTIONS = [None]
for w in (0, 1):
    for d in (-1, 1):
        for s in STATES_8:
            ALL_ACTIONS.append((w, d, s))

print("=================================================================")
print("1. CHECK ALL 4,356 C0-SLOT REDIRECTS FOR ODD TOWERS OR LONG TOWERS")
print("=================================================================")

for start_label, start_st in [("F89(A)", 'A'), ("F89-S1(C)", 'C'), ("F89-S2(F)", 'F'), ("F89-S3(D)", 'D')]:
    odd_tower_machines = []
    other_k_machines = []
    for c0_w in (0, 1):
        for c0_d in (-1, 1):
            for h0 in ALL_ACTIONS:
                for h1 in ALL_ACTIONS:
                    t = dict(base_trans)
                    t[('C', 0)] = (c0_w, c0_d, 'H')
                    t[('H', 0)] = h0
                    t[('H', 1)] = h1
                    r = run_blank(t, start_st=start_st, max_steps=7000)
                    if r[0] == "ODD_TOWER":
                        # Test what this machine does on S([x]) for x=3, 5, 7, 9, 11, 13
                        sx = [run_from_k(t, [x], max_steps=3000, max_k=1) for x in (3, 5, 7, 9)]
                        odd_tower_machines.append(((c0_w, c0_d), h0, h1, r[1], r[2], sx))
                    elif r[0] == "TIMEOUT" and len(r[3]) > 0:
                        # Reached K-configs (not all-odd len>=3) and didn't halt in 7000 steps
                        other_k_machines.append(((c0_w, c0_d), h0, h1, r[3]))
    print(f"\n=== Start {start_label}: ODD_TOWER={len(odd_tower_machines)}, OTHER_K_TIMEOUT={len(other_k_machines)} ===")
    # Check if any ODD_TOWER machine halts on S([x]) or does anything non-standard!
    odd_halts = [m for m in odd_tower_machines if any(s[0] == "HALT" for s in m[5])]
    print(f"  ODD_TOWER machines that HALT on S([x]) for x in (3,5,7,9): {len(odd_halts)}")
    for m in odd_halts:
        print(f"    CHAMP?! C0={m[0]} H0={m[1]} H1={m[2]} tower={m[4]}@{m[3]} sx={[ (s[0], s[1], s[2]) for s in m[5] ]}")
    # Summarize S([3]) behavior of all ODD_TOWER machines
    s3_Map = {}
    for m in odd_tower_machines:
        s3 = m[5][0]
        key = (s3[0], tuple(s3[2]) if isinstance(s3[2], list) else s3[2])
        s3_Map[key] = s3_Map.get(key, 0) + 1
    print(f"  ODD_TOWER S([3]) outcomes: {s3_Map}")
    
    # Also check OTHER_K_TIMEOUT machines: what K-configs are they in, and do any of them halt on S([x])?
    other_with_s_halt = []
    for c0_act, h0, h1, ks in other_k_machines:
        t = dict(base_trans)
        t[('C', 0)] = (c0_act[0], c0_act[1], 'H')
        t[('H', 0)] = h0
        t[('H', 1)] = h1
        # Check if max len of K-config >= 4 and contains non-zero high digits
        max_len = max(len(L) for _, L in ks)
        last_L = ks[-1][1]
        # Check if it's just growing zeros/ones linearly or if it's a real tower reduction
        if len(ks) >= 5:
            # Check if digits are decreasing (like D/B_k) vs just appending zeros/ones
            is_lin_grow = all(len(ks[i+1][1]) >= len(ks[i][1]) and ks[i+1][1][-1] == 0 for i in range(len(ks)-3, len(ks)-1))
            is_1d_2d = (max_len <= 3)
            if not is_lin_grow and not is_1d_2d:
                other_with_s_halt.append((c0_act, h0, h1, max_len, ks[0], ks[-1]))
    print(f"  OTHER_K_TIMEOUT non-linear-grow with max_len>=4: {len(other_with_s_halt)}")
    for c0_act, h0, h1, ml, k0, kl in other_with_s_halt[:20]:
        print(f"    C0={c0_act} H0={h0} H1={h1} max_len={ml} k0={k0[1]}@{k0[0]} kl={kl[1][:8]}@{kl[0]}")
