import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle
from verify_rule_d import parse_tm

def run_accel_v3(tr, k, N, is_232=False, max_iters=5000, allow_collapse=True):
    OFFSET = 200000
    SZ = 400000
    tape = bytearray(SZ)
    left_str = "10"*(2*k-1) + "11001"
    right_str = "100" + "1100"*N + "1"
    full_str = left_str + "1" + right_str
    for i, c in enumerate(full_str):
        if c == '1':
            tape[OFFSET + i] = 1
    lo = OFFSET
    hi = OFFSET + len(full_str) - 1
    h = OFFSET + len(left_str)
    q = 2
    step = 0
    iters = 0
    collapsed = False
    d_const = 58 if is_232 else 56
    MIN_SAFE_H = 2000

    while iters < max_iters:
        iters += 1
        if q == 4 and tape[h] == 0:
            while lo <= hi and tape[lo] == 0: lo += 1
            while hi >= lo and tape[hi] == 0: hi -= 1
            if lo <= hi and h == lo - 1 and h + 4 <= hi:
                if tape[h+1] == 1 and tape[h+2] == 0 and tape[h+3] == 0 and tape[hi] == 1 and tape[hi-1] == 0 and tape[hi-2] == 0:
                    pos = h + 4
                    ok = True
                    num_runs = 0
                    first_run = -1
                    d1 = -1; d2 = -1
                    while pos <= hi - 1:
                        ones = 0
                        while pos <= hi - 1 and tape[pos] == 1:
                            ones += 1
                            pos += 1
                        if ones % 2 != 0 or pos + 1 > hi - 1 or tape[pos] != 0 or tape[pos+1] != 0:
                            ok = False
                            break
                        pos += 2
                        val = ones // 2
                        if num_runs == 0: first_run = val
                        elif num_runs == 1: d1 = val
                        elif num_runs == 2: d2 = val
                        num_runs += 1
                    if ok and num_runs - 1 >= N - 3:
                        return ("K*" if collapsed else "K", step, num_runs - 1, first_run, d1, d2, iters)

            if h < lo:
                zeros_left = h - MIN_SAFE_H
            else:
                p_left = h - 1
                while tape[p_left] == 0:
                    p_left -= 1
                zeros_left = h - 1 - p_left

            # Try Macro 1: Chained Rule D (m = 0) or Borrow B_m (m >= 1)
            if tape[h+1] == 1 and tape[h+2] == 0 and tape[h+3] == 0:
                p = h + 4
                while tape[p] == 1: p += 1
                ones = p - (h + 4)
                if ones % 2 == 0:
                    a = ones // 2
                    pz = p
                    while pz <= hi + 2 and tape[pz] == 0: pz += 1
                    zeros = pz - p
                    if zeros == 2 and tape[pz] == 1 and tape[pz+1] == 1:
                        pr = pz
                        while tape[pr] == 1: pr += 1
                        r = pr - pz
                        if zeros_left >= 4 * a + 4 and h - (4 * a + 4) >= MIN_SAFE_H:
                            while r >= 2 and zeros_left >= 4 * a + 4 and h - (4 * a + 4) >= MIN_SAFE_H:
                                shift = 4 * a + 4
                                step += 12 * a * a + 66 * a + d_const
                                h -= shift
                                zeros_left -= shift
                                a = 3 * a + 3
                                r -= 2
                            if allow_collapse and r >= 2 and h < lo and h - (4 * a + 4) < MIN_SAFE_H:
                                # Tower collapse! All remaining r//2 decrements execute with no 1s on left
                                collapsed = True
                                rem_dec = r // 2
                                r = r % 2
                                # Keep a capped at a_cap = 30 (same parity as after rem_dec decrements, though 2a is always even)
                                # Shift right end back by setting a = 30:
                                # Note: the remaining r ones start at pr - r.
                                # So the two 0s before the remaining r ones are at pr - r - 2 and pr - r - 1.
                                a_cap = 30
                                h = (pr - r - 2) - 2 * a_cap - 4
                                # Zero out everything from old lo to pr - r - 1
                                tape[lo : pr - r] = b'\x00' * ((pr - r) - lo)
                                a = a_cap
                                lo = h + 1
                            tape[h+1] = 1
                            tape[h+2] = 0
                            tape[h+3] = 0
                            tape[h+4 : h+4+2*a] = b'\x01' * (2 * a)
                            tape[h+4+2*a] = 0
                            tape[h+5+2*a] = 0
                            if h + 1 < lo: lo = h + 1
                            continue
                    elif zeros >= 4 and zeros % 2 == 0 and tape[pz] == 1 and tape[pz+1] == 1:
                        m = (zeros // 2) - 1
                        if zeros_left >= 4 * a + 4 and 3 * a + 3 >= m and h - (4 * a + 4) >= MIN_SAFE_H:
                            shift = 4 * a + 4
                            step += 12*a*a + 66*a + 56 + 24*a*m + 22*m - 4*m*m + (2*(m+1) if is_232 else 0)
                            h -= shift
                            tape[h+1] = 1
                            tape[h+2] = 0
                            tape[h+3] = 0
                            pos = h + 4
                            for _ in range(m):
                                tape[pos] = 1; tape[pos+1] = 1; tape[pos+2] = 0; tape[pos+3] = 0
                                pos += 4
                            rem_ones = 2 * (3 * a + 3 - m)
                            tape[pos : pos + rem_ones] = b'\x01' * rem_ones
                            pos += rem_ones
                            tape[pos] = 0
                            tape[pos+1] = 0
                            if h + 1 < lo: lo = h + 1
                            continue

            # Try Macro 2: Expand E0
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
                        tape[h + m + c + 1] = 0
                        tape[h + m + c + 2] = 0
                        h = h_new
                        if h + 1 < lo: lo = h + 1
                        step += c * (2 * m + 10) + 3 * c * (c - 1)
                        continue

        # Try Macro 3: Run-skip on B1, E1, F1
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
            return ("H*" if collapsed else "H", step + 1, q, b, 0, 0, iters)
        tape[h] = 1 if act[0] == '1' else 0
        h += 1 if act[1] == 'R' else -1
        q = ord(act[2]) - 65
        step += 1
        if h < 100 or h >= SZ - 100:
            return ("T", step, q, b, 0, 0, iters)
        if h - 2 < lo: lo = h - 2
        if h + 2 > hi: hi = h + 2

    return ("T", step, q, tape[h], 0, 0, iters)

for name, tm in [
    ("KKHKHK_231", "1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_0RB0RI_0LG---"),
    ("KHTKHT_231", "1RB0RG_1RC1RB_0RD0RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_1LC0RI_1LC---"),
    ("KKTKKT_231_L", "1RB0RG_1RC1RB_0RD0LH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_---0LI_1RI0RG"),
    ("KKTKKT_231_R", "1RB0RG_1RC1RB_0RD0RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_1RI1RD_1RD---"),
]:
    print(f"=== {name} ===")
    tr = parse_tm(tm)
    for k in range(1, 7):
        res = run_accel_v3(tr, k, 6)
        print(f"  k={k}: {res}")
