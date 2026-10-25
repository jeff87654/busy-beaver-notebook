import sys

def parse_tm(tm_str):
    parts = tm_str.strip().split('_')
    tr = []
    for p in parts:
        tr.append(p[:3])
        tr.append(p[3:6])
    return tr

def run_ackermann_sim_trace(tr, k, N, is_232=False, max_iters=30000):
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
    d_const = 58 if is_232 else 56
    collapsed = False
    ack_jumps = 0
    jump_log = []

    for iters in range(1, max_iters + 1):
        if q == 4 and tape[h] == 0:
            while lo <= hi and tape[lo] == 0: lo += 1
            while hi >= lo and tape[hi] == 0: hi -= 1
            if lo <= hi and h == lo - 1 and h + 4 <= hi:
                if tape[h+1] == 1 and tape[h+2] == 0 and tape[h+3] == 0 and tape[hi] == 1 and tape[hi-1] == 0 and tape[hi-2] == 0:
                    pos = h + 4; ok = True; vals = []
                    while pos <= hi - 1:
                        ones = 0
                        while pos <= hi - 1 and tape[pos] == 1: ones += 1; pos += 1
                        if ones % 2 != 0 or pos + 1 > hi - 1 or tape[pos] != 0 or tape[pos+1] != 0: ok = False; break
                        pos += 2; vals.append(ones // 2)
                    if ok and len(vals) - 1 >= max(2, N - 2*k - 3):
                        k_len = len(vals) - 1
                        parity_I = sum(vals) % 2
                        return ("K*" if collapsed else "K", step, k_len - N, parity_I, vals[0], ack_jumps, iters, jump_log)

                if tape[h+1] == 1 and tape[h+2] == 0 and tape[h+3] == 0:
                    pos = h + 4
                    even_vals = []
                    odd_pos = -1
                    odd_len = -1
                    while pos <= hi:
                        ones = 0
                        p_start = pos
                        while pos <= hi and tape[pos] == 1:
                            ones += 1; pos += 1
                        if ones % 2 == 1:
                            odd_pos = p_start
                            odd_len = ones
                            break
                        if pos + 1 <= hi and tape[pos] == 0 and tape[pos+1] == 0:
                            even_vals.append(ones // 2)
                            pos += 2
                        else:
                            break
                    if len(even_vals) >= 1 and odd_pos != -1:
                        s_digits = len(even_vals) - 1
                        d_odd = odd_len // 2
                        has_nonzero_even_digit = any(x > 0 for x in even_vals[1:])
                        if (s_digits >= 1 and has_nonzero_even_digit and (odd_pos < hi or d_odd >= 1)) or (s_digits == 0 and d_odd >= 1 and (even_vals[0] >= 100 or d_odd >= 6)):
                            collapsed = True
                            ack_jumps += 1
                            nz_evens = [(idx, val) for idx, val in enumerate(even_vals[1:], 1) if val > 0]
                            max_nz_idx = max((idx for idx, _ in nz_evens), default=0)
                            jump_log.append({
                                "j": ack_jumps,
                                "type": "A",
                                "s_digits": s_digits,
                                "max_nz_idx": max_nz_idx,
                                "a": even_vals[0],
                                "nz_evens": nz_evens[:5],
                                "d_odd": d_odd,
                            })
                            total_parity = (sum(even_vals) + d_odd) % 2
                            base_u = max(60, 6 * ((s_digits + 10) // 6 + 1))
                            if base_u % 12 != 0: base_u += 6
                            u_cap = base_u + 6 * total_parity
                            rem_one_pos = odd_pos + 2 * d_odd
                            zeros_span = 2 * s_digits + 2
                            new_h = rem_one_pos - zeros_span - u_cap - 4
                            tape[lo : rem_one_pos] = b'\x00' * (rem_one_pos - lo)
                            h = new_h
                            tape[h+1] = 1; tape[h+2] = 0; tape[h+3] = 0
                            tape[h+4 : h+4+u_cap] = b'\x01' * u_cap
                            lo = h + 1
                            step += 1000000000
                            continue

            if h < lo: zeros_left = h - MIN_SAFE_H
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
                            step += 3 * u * u + 33 * u + d_const
                            h -= shift; zeros_left -= shift
                            u = 3 * u + 6; r -= 2
                        if r >= 2 and h < lo and h - (2 * u + 4) < MIN_SAFE_H:
                            collapsed = True; ack_jumps += 1
                            rem_dec = r // 2; r = r % 2
                            jump_log.append({
                                "j": ack_jumps,
                                "type": "B",
                                "s_digits": 0,
                                "max_nz_idx": 0,
                                "a": u // 2,
                                "nz_evens": [],
                                "d_odd": rem_dec,
                            })
                            u_cap = (60 + 6 * (((u // 2) + rem_dec) % 2)) if (u % 2 == 0) else 63
                            new_h = (pr - r - 2) - u_cap - 4
                            if lo < pr - r: tape[lo : pr - r] = b'\x00' * ((pr - r) - lo)
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
                        step += 3*u*u + 33*u + 56 + 12*u*m + 22*m - 4*m*m + (2*(m+1) if is_232 else 0)
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
            return ("H*" if collapsed else "H", step + 1, f"{chr(65+q)}{b}", 0, 0, ack_jumps, iters, jump_log)
        tape[h] = 1 if act[0] == '1' else 0
        h += 1 if act[1] == 'R' else -1
        q = ord(act[2]) - 65
        step += 1
        if h - 2 < lo: lo = h - 2
        if h + 2 > hi: hi = h + 2
    return ("T", step, 0, 0, 0, ack_jumps, max_iters, jump_log)

MACHINES = [
    ("P3_1LG0LI_1LH--- (K*,K*,H*)", "1RB0RG_1RC1RB_0RD0LH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_1LG0LI_1LH---", False),
    ("P2_---0RI_1RF1LG (H*,K*)",    "1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_---0RI_1RF1LG", False),
    ("P5_---0LI_1LG0LH (K*x4,H*)",  "1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_---0LI_1LG0LH", False),
    ("P6_---0LI_0RI0RG (H*,K*x5)",  "1RB0RG_1RC1RB_0RD0RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_---0LI_0RI0RG", False),
    ("CASCADE_---1LI_1RB1LH",       "1RB0RG_1RC1RB_0RD0LH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_---1LI_1RB1LH", False),
    ("CAP_---0LI_1RF1LC",           "1RB0RG_1RC1RB_0RD0LH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_---0LI_1RF1LC", False),
    ("CAP_R8_0RE0LF (232)",         "1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_1LC0RB_---1RI_0RE0LF", True),
    ("CAP_R8_1RA0LF (232)",         "1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_1LC0RB_---1RI_1RA0LF", True),
    ("CAP_1LD0LI_1LH---",           "1RB0RG_1RC1RB_0RD0RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_1LD0LI_1LH---", False),
]

for label, tm, is_232 in MACHINES:
    print(f"\n=======================================================")
    print(f"MACHINE: {label} | {tm}")
    tr = parse_tm(tm)
    for k in [8, 12, 16, 20, 21, 24, 30]:
        res = run_ackermann_sim_trace(tr, k, 2*k + 10, is_232=is_232, max_iters=30000)
        kind, step, dL, I, a, c, iters, jlog = res
        s_list = [j["s_digits"] for j in jlog]
        max_nz_list = [j["max_nz_idx"] for j in jlog]
        d_odd_list = [j["d_odd"] for j in jlog]
        print(f"  k={k:2d}: kind={kind:2s} dL/slot={str(dL):3s} I={I} a={a:3d} c={c:2d} | s_digits={s_list} | max_nz_idx={max_nz_list} | d_odd={d_odd_list}")
        if k == 20 and jlog:
            for j in jlog[:10]:
                print(f"    jump #{j['j']}: type={j['type']} s_digits={j['s_digits']} max_nz_idx={j['max_nz_idx']} a={j['a']} nz_evens={j['nz_evens']} d_odd={j['d_odd']}")
