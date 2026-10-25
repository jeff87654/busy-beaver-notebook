import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle
from verify_rule_d import parse_tm

tm = "1RB0RG_1RC1RB_0RD0LH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_---1LI_1RB1LH"
tr = parse_tm(tm)

def trace_kp(tr, k, N, max_iters=200000):
    OFFSET = 200000
    SZ = 400000
    tape = bytearray(SZ)
    left_str = "10"*(2*k-1) + "11001"
    right_str = "100" + "1100"*N + "1"
    full_str = left_str + "1" + right_str
    for i, c in enumerate(full_str):
        if c == '1': tape[OFFSET + i] = 1
    lo = OFFSET; hi = OFFSET + len(full_str) - 1
    h = OFFSET + len(left_str); q = 2; step = 0
    MIN_SAFE_H = 2000
    events = []

    for iters in range(1, max_iters + 1):
        if q == 4 and tape[h] == 0:
            while lo <= hi and tape[lo] == 0: lo += 1
            while hi >= lo and tape[hi] == 0: hi -= 1
            # Check if we hit C1/H/I recently or if h == lo - 1
            if lo <= hi and h + 4 <= hi and tape[h+1] == 1 and tape[h+2] == 0 and tape[h+3] == 0:
                # Check if right side is formatted K-tower
                pos = h + 4
                ok = True
                vals = []
                while pos <= hi - 1:
                    ones = 0
                    while pos <= hi - 1 and tape[pos] == 1:
                        ones += 1; pos += 1
                    if ones % 2 != 0 or pos + 1 > hi - 1 or tape[pos] != 0 or tape[pos+1] != 0:
                        ok = False; break
                    pos += 2
                    vals.append(ones // 2)
                if ok and len(vals) >= 2 and tape[hi] == 1 and tape[hi-1] == 0 and tape[hi-2] == 0:
                    l_prefix = "".join(str(tape[i]) for i in range(lo, h)) if lo < h else ""
                    # Count trailing 1s in vals
                    t1 = 0
                    while t1 < len(vals) and vals[len(vals) - 1 - t1] == 1:
                        t1 += 1
                    front_vals = vals[:len(vals) - t1]
                    events.append((iters, step, l_prefix, front_vals, t1))
                    if l_prefix == "" and len(vals) - 1 >= N - 2*k - 3:
                        return "K", iters, step, events

            if h < lo:
                zeros_left = h - MIN_SAFE_H
            else:
                p_left = h - 1
                while tape[p_left] == 0: p_left -= 1
                zeros_left = h - 1 - p_left

            if tape[h+1] == 1 and tape[h+2] == 0 and tape[h+3] == 0:
                p = h + 4
                while tape[p] == 1: p += 1
                u = p - (h + 4)
                pz = p
                while pz <= hi + 2 and tape[pz] == 0: pz += 1
                zeros = pz - p
                if zeros == 2 and tape[pz] == 1 and tape[pz+1] == 1:
                    pr = pz
                    while tape[pr] == 1: pr += 1
                    r = pr - pz
                    if zeros_left >= 2 * u + 4 and h - (2 * u + 4) >= MIN_SAFE_H:
                        while r >= 2 and zeros_left >= 2 * u + 4 and h - (2 * u + 4) >= MIN_SAFE_H:
                            shift = 2 * u + 4
                            step += 3 * u * u + 33 * u + 56
                            h -= shift; zeros_left -= shift
                            u = 3 * u + 6; r -= 2
                        if r >= 2 and h < lo and h - (2 * u + 4) < MIN_SAFE_H:
                            rem_dec = r // 2
                            r = r % 2
                            u_cap = (60 + 6 * (((u // 2) + rem_dec) % 2)) if (u % 2 == 0) else 63
                            new_h = (pr - r - 2) - u_cap - 4
                            if lo < pr - r:
                                tape[lo : pr - r] = b'\x00' * ((pr - r) - lo)
                            h = new_h; u = u_cap; lo = h + 1
                        tape[h+1] = 1; tape[h+2] = 0; tape[h+3] = 0
                        tape[h+4 : h+4+u] = b'\x01' * u
                        tape[h+4+u] = 0; tape[h+5+u] = 0
                        if h + 1 < lo: lo = h + 1
                        continue
                elif zeros >= 4 and zeros % 2 == 0 and tape[pz] == 1 and tape[pz+1] == 1:
                    m = (zeros // 2) - 1
                    if zeros_left >= 2 * u + 4 and 3 * u + 6 >= 2 * m and h - (2 * u + 4) >= MIN_SAFE_H:
                        shift = 2 * u + 4
                        step += 3*u*u + 33*u + 56 + 12*u*m + 22*m - 4*m*m
                        h -= shift
                        tape[h+1] = 1; tape[h+2] = 0; tape[h+3] = 0
                        pos = h + 4
                        for _ in range(m):
                            tape[pos] = 1; tape[pos+1] = 1; tape[pos+2] = 0; tape[pos+3] = 0; pos += 4
                        rem_ones = 3 * u + 6 - 2 * m
                        tape[pos : pos + rem_ones] = b'\x01' * rem_ones
                        pos += rem_ones
                        tape[pos] = 0; tape[pos+1] = 0
                        if h + 1 < lo: lo = h + 1
                        continue

            if zeros_left >= 2 and tape[h+1] == 1:
                p = h + 1
                while tape[p] == 1: p += 1
                m = p - (h + 1)
                if tape[p] == 0 and tape[p+1] == 0 and tape[p+2] == 1:
                    p2 = p + 2
                    while tape[p2] == 1: p2 += 1
                    n = p2 - (p + 2)
                    c = min(n, zeros_left // 2)
                    if c > 0 and h - 2 * c >= MIN_SAFE_H:
                        h_new = h - 2 * c
                        tape[h_new + 1 : h + m + c + 1] = b'\x01' * (m + 3 * c)
                        tape[h + m + c + 1] = 0; tape[h + m + c + 2] = 0
                        h = h_new
                        if h + 1 < lo: lo = h + 1
                        step += c * (2 * m + 10) + 3 * c * (c - 1)
                        continue

        b = tape[h]
        if b == 1:
            if q == 1:
                p = h + 1
                while tape[p] == 1: p += 1
                step += p - h; h = p
                if h + 2 > hi: hi = h + 2
                continue
            elif q == 4 or q == 5:
                p = h - 1
                while tape[p] == 1: p -= 1
                step += h - p; h = p
                if h - 2 < lo: lo = h - 2
                continue

        slot = 2 * q + b
        act = tr[slot]
        if act == "---":
            return f"H({chr(65+q)}{b})", iters, step + 1, events
        tape[h] = 1 if act[0] == '1' else 0
        h += 1 if act[1] == 'R' else -1
        q = ord(act[2]) - 65
        step += 1
        if h - 2 < lo: lo = h - 2
        if h + 2 > hi: hi = h + 2

    return "T", max_iters, step, events

for k in range(1, 9):
    N = 2 * k + 6
    out, iters, step, evs = trace_kp(tr, k, N, max_iters=300000)
    print(f"\n=== k = {k} (N = {N}): outcome = {out} at iter = {iters}, step = {step}, KP_events = {len(evs)} ===")
    for e in evs[:12]:
        print(f"  iter={e[0]:6d} step={e[1]:14d}: L='{e[2]}' front={e[3]} + 1^{e[4]}")
    if len(evs) > 12:
        print("  ...")
        for e in evs[-5:]:
            print(f"  iter={e[0]:6d} step={e[1]:14d}: L='{e[2]}' front={e[3]} + 1^{e[4]}")
