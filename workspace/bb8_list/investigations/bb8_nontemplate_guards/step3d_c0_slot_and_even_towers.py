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

def run_multi_k(trans, L_init, max_steps=150000, max_k=80):
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

print("=================================================================")
print("1. EXTENDED TRACE OF EVEN-TOWER GUARD REDIRECTS AT x=3")
print("=================================================================")

even_cases = [
    ("B0:0", ("B", 0, 0), (0, -1, 'H')),
    ("B0:0", ("B", 0, 0), (0, 1, 'C')),
    ("B0:0", ("B", 0, 0), (1, -1, 'C')),
    ("B0:0", ("B", 0, 0), (1, -1, 'H')),
    ("C0:0", ("C", 0, 0), (0, -1, 'F')),
    ("C0:0", ("C", 0, 0), (1, 1, 'D')),
    ("C0:1", ("C", 0, 1), (0, -1, 'G')),
    ("C0:1", ("C", 0, 1), (0, 1, 'A')),
    ("C0:1", ("C", 0, 1), (1, 1, 'F')),
]

for label, (st_x, sym_x, s_guard), act in even_cases:
    old_w, old_d, old_nxt = base_trans[(st_x, sym_x)]
    t = dict(base_trans)
    t[(st_x, sym_x)] = (old_w, old_d, 'H')
    t[('H', 1 - s_guard)] = base_trans[(old_nxt, 1 - s_guard)]
    t[('H', s_guard)] = act
    r = run_multi_k(t, [3], max_steps=300000, max_k=120)
    print(f"\n[{label} -> {act}] on [3]: {r[0]} at step {r[1]} (K count={len(r[3])})")
    for stp, L in r[3]:
        if len(L) <= 3 or stp == r[3][0][0] or stp == r[3][-1][0]:
            print(f"  step {stp:6d}: L={L} (len={len(L)})")

print("\n=================================================================")
print("2. SCREEN ALL 4,356 C0-SLOT REDIRECTS (C0 -> w d H, H0, H1)")
print("=================================================================")

ALL_ACTIONS = [None]
for w in (0, 1):
    for d in (-1, 1):
        for s in STATES_8:
            ALL_ACTIONS.append((w, d, s))

# First test each of the 4,356 machines on [1] and [3] with max_steps=5000, max_k=1
# to filter out immediate E1 halts (0 K-events) and immediate E1 timeouts (0 K-events)
selective_or_multi = []
counts = {}
for c0_w in (0, 1):
    for c0_d in (-1, 1):
        for h0 in ALL_ACTIONS:
            for h1 in ALL_ACTIONS:
                t = dict(base_trans)
                t[('C', 0)] = (c0_w, c0_d, 'H')
                t[('H', 0)] = h0
                t[('H', 1)] = h1
                
                r1 = run_multi_k(t, [1], max_steps=4000, max_k=1)
                r3 = run_multi_k(t, [3], max_steps=4000, max_k=1)
                
                k1, k3 = r1[0], r3[0]
                counts[(k1, k3)] = counts.get((k1, k3), 0) + 1
                if k1 == "MAX_K" or k3 == "MAX_K":
                    # Reached at least 1 K-config! Run deeper on [1], [3], [5]
                    r1_deep = run_multi_k(t, [1], max_steps=30000, max_k=30)
                    r3_deep = run_multi_k(t, [3], max_steps=30000, max_k=30)
                    r5_deep = run_multi_k(t, [5], max_steps=30000, max_k=30)
                    if any(r[0] == "HALT" for r in (r1_deep, r3_deep, r5_deep)):
                        selective_or_multi.append(((c0_w, c0_d), h0, h1, r1_deep, r3_deep, r5_deep))

print(f"4,356 C0-slot redirects initial (k1, k3) summary: {counts}")
print(f"Machines reaching >=1 K-config on [1]/[3] and later HALTING on [1],[3], or [5]: {len(selective_or_multi)}")
for c0_act, h0, h1, r1, r3, r5 in selective_or_multi[:40]:
    print(f"  C0={c0_act} H0={h0} H1={h1}:")
    for x, r in [(1, r1), (3, r3), (5, r5)]:
        ks = [L for _, L in r[3][:5]]
        print(f"    x={x}: {r[0]}@{r[1]}({r[2]}) K_len={len(r[3])} first_Ks={ks}")
