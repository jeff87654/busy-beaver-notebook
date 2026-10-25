import os, re

WORKDIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_f89_and_cascade"

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

def check_k(tape, h, s, mv):
    if s != 'D' or h != mv: return None
    mx = max([k for k, v in tape.items() if v] + [h])
    bits = [tape.get(i, 0) for i in range(h, mx + 1)]
    while bits and bits[-1] == 0: bits.pop()
    if len(bits) < 4 or bits[:4] != [0, 0, 0, 1]: return None
    i = 3; L = []
    while i < len(bits):
        if bits[i] != 1: return None
        i += 1; d = 0
        while i + 1 < len(bits) and bits[i] == 0 and bits[i+1] == 1:
            d += 1; i += 2
        L.append(d)
    return L

def write_k(L):
    bits = [0, 0, 0]
    for d in L:
        bits.append(1)
        for _ in range(d):
            bits.extend([0, 1])
    return {i: b for i, b in enumerate(bits) if b}

def cap_odd(v):
    return v if v <= 85 else 25 + (v - 25) % 60

def step_core_exact(L):
    """Apply exact 12-transition core macro-steps (D, B_k, T_k, ZD, Z_2, E_2) with O(1) sub-tower collapse."""
    if len(L) < 2: return False
    # Count leading odd digits
    m_odd = 0
    while m_odd < len(L) and L[m_odd] > 0 and L[m_odd] % 2 == 1:
        m_odd += 1
    if m_odd == len(L) and m_odd >= 4:
        L[:] = [61]
        return True
    if m_odd >= 4 and m_odd < len(L):
        # Collapse leading odd sub-tower of height >= 4 to [57, 1, ...] (since [57, 1] -> [61])
        L[:] = [57, 1] + L[m_odd:]
        return True

    a = L[0]
    if a == 2 and len(L) >= 3 and L[1] == 0 and L[2] == 1:
        k = 0
        while 2 + k < len(L) and L[2 + k] == 1: k += 1
        if 2 + k == len(L):
            L[:] = [3, 3] if k == 1 else [3, 0] + [1]*(k-2) + [4]
            return True
        elif L[2 + k] >= 2:
            d = L[2 + k]
            L[:] = [3, 0] + [1]*(k-1) + [4, d - 2] + L[3 + k:]
            return True
    if a <= 0 or a % 2 == 0: return False
    if L[1] >= 2:
        q = (L[1] - 1) // 2 if L[1] % 2 == 1 else L[1] // 2
        if q > 0:
            L[0] = cap_odd(a + 4 * q)
            L[1] -= 2 * q
            return True
    if L[1] == 1:
        k = 0
        while 1 + k < len(L) and L[1 + k] == 1: k += 1
        na = cap_odd(a + 4)
        if 1 + k == len(L):
            L[:] = [1]*(k - 1) + [na]
            return True
        elif L[1 + k] >= 2:
            d = L[1 + k]
            L[:] = [1]*k + [na, d - 2] + L[2 + k:]
            return True
    if L[1] == 0 and len(L) >= 3:
        # Check how many odd digits follow [a, 0, ...]
        m2 = 0
        while 2 + m2 < len(L) and L[2 + m2] > 0 and L[2 + m2] % 2 == 1:
            m2 += 1
        if m2 >= 3 or (m2 == 2 and L[3] >= 3):
            # Exact universal residue for [a, 0, d_1, ..., d_{m2}, R] -> [87, 0, 1, R] (87 == 27 mod 60)
            L[:] = [87, 0, 1] + L[2 + m2:]
            return True
        if L[2] >= 2:
            d = L[2]; q = d // 2
            cur = a
            for _ in range(q):
                cur = cap_odd(2 * cur + 5)
            L[0] = cur; L[2] = d - 2 * q
            return True
        elif L[2] == 1:
            k = 0
            while 2 + k < len(L) and L[2 + k] == 1: k += 1
            if 2 + k == len(L):
                L[:] = [cap_odd(2 * a + 5), 0] if k == 1 else [3, 0] + [1]*(k-2) + [cap_odd(a + 2)]
                return True
            elif L[2 + k] >= 2:
                d = L[2 + k]
                L[:] = [3, 0] + [1]*(k-1) + [cap_odd(a + 2), d - 2] + L[3 + k:]
                return True
    return False

top_tms = [
    ("Line29_C01_0RI_0LC", "1RB0RE_0RC0RI_1LH0RG_1RA0RF_1LF0LD_1LD0LE_1RC1RE_1RA0LF_---0LC"),
    ("Line96_C01_1LI_0LI1LC", "1RB0RE_0RC---_1LH0RG_1RA0RF_1LF0LD_1LD0LE_1RC1RE_1RA1LI_0LI1LC"),
    ("Line98_C01_0LC_1LI_1LH", "1RB0RE_0RC0LC_1LH0RG_1RA0RF_1LF0LD_1LD0LE_1RC1RE_1RA1LI_1LH---"),
]

for label, tm in top_tms:
    print("\n" + "="*95)
    print(f"{label}: {tm}")
    t = parse_tm(tm)
    for x in [1, 3, 5, 7, 9, 11, 13, 15, 21, 61]:
        tape = write_k([x]); h = 0; s = 'D'; mv = 0
        ks = [[x]]
        for step in range(1, 15000):
            c = tape.get(h, 0); tr = t.get((s, c))
            if tr is None:
                print(f"  S([{x:2d}]): HALT at {s}{c} step={step:5d} k_ev={len(ks):2d} seq={ks[:4]} ... {ks[-2:] if len(ks)>4 else []}")
                break
            w, d, n = tr
            if w: tape[h] = 1
            else: tape.pop(h, None)
            h += d; s = n
            if h < mv:
                mv = h; L = check_k(tape, h, s, mv)
                if L is not None:
                    ks.append(list(L))
                    changed = False
                    iters = 0
                    while len(L) >= 2 and iters < 50 and step_core_exact(L):
                        changed = True
                        iters += 1
                    if changed:
                        ks.append(list(L))
                        tape = write_k(L); h = 0; mv = 0; s = 'D'
                    if len(ks) > 60:
                        print(f"  S([{x:2d}]): MAX_K seq={ks[:4]} ... {ks[-2:]}")
                        break
        else:
            print(f"  S([{x:2d}]): TIMEOUT k_ev={len(ks)} seq={ks[:4]} ... {ks[-2:] if len(ks)>4 else []}")
