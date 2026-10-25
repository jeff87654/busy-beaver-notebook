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

def run_blank(trans, start_st='A', max_steps=30000):
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
    return ("TIMEOUT", max_steps, None, k_list)

base_trans = parse_tm(F89_CODE)

ALL_ACTIONS = [None]
for w in (0, 1):
    for d in (-1, 1):
        for s in STATES_8:
            ALL_ACTIONS.append((w, d, s))

print("=================================================================")
print("1. BLANK-TAPE SCREEN OF ALL 4,356 C0-SLOT REDIRECTS (STARTS A, C, F, D)")
print("=================================================================")

for start_label, start_st in [("F89(A)", 'A'), ("F89-S1(C)", 'C'), ("F89-S2(F)", 'F'), ("F89-S3(D)", 'D')]:
    halts_over_200 = []
    max_halt = 0
    total_halts = 0
    for c0_w in (0, 1):
        for c0_d in (-1, 1):
            for h0 in ALL_ACTIONS:
                for h1 in ALL_ACTIONS:
                    t = dict(base_trans)
                    t[('C', 0)] = (c0_w, c0_d, 'H')
                    t[('H', 0)] = h0
                    t[('H', 1)] = h1
                    r = run_blank(t, start_st=start_st, max_steps=15000)
                    if r[0] == "HALT":
                        total_halts += 1
                        if r[1] > max_halt:
                            max_halt = r[1]
                        if r[1] > 200:
                            halts_over_200.append(((c0_w, c0_d), h0, h1, r[1], r[2], r[3]))
    print(f"\n=== Start {start_label}: total_halts={total_halts}/4356, max_halt={max_halt}, halts_>200={len(halts_over_200)} ===")
    for c0_act, h0, h1, stp, sl, ks in sorted(halts_over_200, key=lambda x: -x[3])[:25]:
        print(f"  step={stp:5d} ({sl}) C0={c0_act} H0={h0} H1={h1} | K_cnt={len(ks)} Ks={[L for _,L in ks[:5]]}..{[L for _,L in ks[-2:]]}")
