import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle
from verify_rule_d import parse_tm, run_base

def run_accel_v2(tr, k, N, is_232=False, max_iters=200000):
    OFFSET = 300000
    SZ = 600000
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
    d_const = 58 if is_232 else 56
    MIN_SAFE_H = 100

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
                    while pos <= hi - 1:
                        ones = 0
                        while pos <= hi - 1 and tape[pos] == 1:
                            ones += 1
                            pos += 1
                        if ones % 2 != 0 or pos + 1 > hi - 1 or tape[pos] != 0 or tape[pos+1] != 0:
                            ok = False
                            break
                        pos += 2
                        num_runs += 1
                    if ok and num_runs - 1 >= N - 3:
                        out_tape = {i - OFFSET: 1 for i in range(lo, hi+1) if tape[i] == 1}
                        return ("K", step, q, 0, h - OFFSET, out_tape, iters)

            # Compute exact zeros_left
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
                    if zeros_left >= 4 * a + 4:
                        pz = p
                        while pz <= hi + 2 and tape[pz] == 0: pz += 1
                        zeros = pz - p
                        if zeros == 2 and tape[pz] == 1 and tape[pz+1] == 1:
                            # Chained Rule D!
                            pr = pz
                            while tape[pr] == 1: pr += 1
                            r = pr - pz
                            while r >= 2 and zeros_left >= 4 * a + 4 and h - (4 * a + 4) >= MIN_SAFE_H:
                                shift = 4 * a + 4
                                step += 12 * a * a + 66 * a + d_const
                                h -= shift
                                zeros_left -= shift
                                a = 3 * a + 3
                                r -= 2
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
                            if 3 * a + 3 >= m and h - (4 * a + 4) >= MIN_SAFE_H:
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

            # Try Macro 2: Expand E0 (0^(2c) [E0] 1^m 00 1^n -> [E0] 1^(m+3c) 00 1^(n-c))
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

        # Try Macro 3: Run-skip on B1 (1RB), E1 (1LE), F1 (1LF)
        b = tape[h]
        if b == 1:
            if q == 1: # B1 = 1RB
                p = h + 1
                while tape[p] == 1: p += 1
                d = p - h
                h = p
                step += d
                if h + 2 > hi: hi = h + 2
                continue
            elif q == 4 or q == 5: # E1 = 1LE, F1 = 1LF
                p = h - 1
                while tape[p] == 1: p -= 1
                d = h - p
                h = p
                step += d
                if h - 2 < lo: lo = h - 2
                continue

        slot = 2 * q + b
        act = tr[slot]
        if act == "---":
            out_tape = {i - OFFSET: 1 for i in range(lo, hi+1) if tape[i] == 1}
            return ("H", step + 1, q, b, h - OFFSET, out_tape, iters)
        tape[h] = 1 if act[0] == '1' else 0
        h += 1 if act[1] == 'R' else -1
        q = ord(act[2]) - 65
        step += 1
        if h - 2 < lo: lo = h - 2
        if h + 2 > hi: hi = h + 2

    out_tape = {i - OFFSET: 1 for i in range(lo, hi+1) if tape[i] == 1}
    return ("T", step, q, tape[h], h - OFFSET, out_tape, iters)

for name, tm, is_232 in [
    ("KKHKHK_231", "1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_0RB0RI_0LG---", False),
    ("KKHKHK_232", "1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_1LC0RB_0RB1RI_0LD---", True),
    ("KHTKHT_231", "1RB0RG_1RC1RB_0RD0RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_1LC0RI_1LC---", False),
    ("KKTKKT_231", "1RB0RG_1RC1RB_0RD0LH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_---0LI_1RI0RG", False),
]:
    print(f"=== {name} ===")
    tr = parse_tm(tm)
    for k in [1, 2, 3, 4, 5]:
        r_base = run_base(tr, k, 6, max_steps=100000)
        r_acc = run_accel_v2(tr, k, 6, is_232=is_232)
        match = (r_base[0] == r_acc[0] and r_base[1] == r_acc[1] and r_base[2:5] == r_acc[2:5] and r_base[5] == r_acc[5])
        print(f"  k={k}: kind={r_acc[0]} step={r_acc[1]:6d} (exp {r_base[1]:6d}) iters={r_acc[6]:4d} | exact_match={match}")
