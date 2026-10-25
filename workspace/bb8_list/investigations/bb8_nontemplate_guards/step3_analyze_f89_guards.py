import os, sys

F89_CODE = "1RB0RE_0RC---_1LD0RG_1RA0RF_1LF0LD_1LD0LE_1RC1RE"

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
    # K-config: [D on a never-visited cell] 0 0 [1 (01)^d1] ... [1 (01)^dn]
    if state != 'D' or head != min_vis:
        return None
    mx = max(tape.keys()) if tape else head
    bits = [tape.get(i, 0) for i in range(head, mx + 1)]
    while bits and bits[-1] == 0:
        bits.pop()
    if len(bits) < 4 or bits[0] != 0 or bits[1] != 0 or bits[2] != 0 or bits[3] != 1:
        return None
    # Parse [1 (01)^d1] [1 (01)^d2] ...
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

print("=================================================================")
print("1. TRACE F89 FROM STARTS A (F89), C (S1), F (S2), D (S3)")
print("=================================================================")

trans = parse_tm(F89_CODE)
for label, start_st in [("F89 (start A)", 'A'), ("F89-S1 (start C)", 'C'), ("F89-S2 (start F)", 'F'), ("F89-S3 (start D)", 'D')]:
    tape = {}
    head = 0
    st = start_st
    min_vis = 0
    print(f"\n[{label}]")
    s_events = []
    k_events = []
    for step in range(0, 6000):
        if step > 0:
            L = check_k_config(tape, head, st, min_vis)
            if L is not None:
                k_events.append((step, L))
                if len(L) <= 5 or step in (13, 162, 4679) or all(x % 2 == 1 for x in L) and len(k_events) <= 15:
                    print(f"  step {step:4d}: K-config L={L} (len={len(L)}, all_odd={all(x%2==1 for x in L)})")
        cur = tape.get(head, 0)
        slot = f"{st}{cur}"
        w, d, nxt = trans[(st, cur)]
        tape[head] = w
        head += d
        st = nxt
        nxt_sym = tape.get(head, 0)
        pair = f"{slot}:{nxt_sym}"
        if pair in ("B0:0", "C0:0", "C0:1", "G0:0") or slot == "C0":
            s_events.append((step + 1, slot, pair))
        if head < min_vis:
            min_vis = head
    print(f"  Total S-only events in 6000 steps: {len(s_events)}")
    for ev in s_events[:15]:
        print(f"    step {ev[0]:4d}: slot={ev[1]} pair={ev[2]}")
    if len(s_events) > 15:
        print(f"    ... and {len(s_events)-15} more; last 5: {s_events[-5:]}")
