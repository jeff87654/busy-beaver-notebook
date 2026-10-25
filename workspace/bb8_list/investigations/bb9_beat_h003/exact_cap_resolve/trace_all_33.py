import sys

def parse_tm(s):
    tr = {}
    for q_idx, part in enumerate(s.split('_')):
        q = chr(ord('A') + q_idx)
        for b in (0, 1):
            sub = part[3*b:3*b+3]
            if sub == '---':
                tr[(q, b)] = None
            else:
                tr[(q, b)] = (int(sub[0]), 1 if sub[1] == 'R' else -1, sub[2])
    return tr

def format_tape(tape, lo, hi, h, q):
    while lo <= hi and tape.get(lo, 0) == 0: lo += 1
    while hi >= lo and tape.get(hi, 0) == 0: hi -= 1
    if lo > hi:
        return f"[{q}0]"
    p = min(lo, h)
    end = max(hi, h)
    blocks = []
    while p <= end:
        if p == h:
            blocks.append(f"[{q}{tape.get(h, 0)}]")
            p += 1
            continue
        b = tape.get(p, 0)
        c = 0
        while p <= end and p != h and tape.get(p, 0) == b:
            c += 1
            p += 1
        blocks.append(f"{b}^{c}" if c > 2 else str(b)*c)
    if len(blocks) > 24:
        blocks = blocks[:18] + ["..."] + blocks[-4:]
    return " ".join(blocks)

def trace_machine(tm_str, k, N, max_iters=5000, verbose=True):
    tr = parse_tm(tm_str)
    tape = {}
    pos = 0
    for _ in range(2 * k - 1):
        tape[pos] = 1; pos += 1
        tape[pos] = 0; pos += 1
    for b in [1, 1, 0, 0, 1]:
        tape[pos] = b; pos += 1
    h = pos
    for b in [1, 1, 0, 0]:
        tape[pos] = b; pos += 1
    for _ in range(N):
        for b in [1, 1, 0, 0]:
            tape[pos] = b; pos += 1
    tape[pos] = 1
    lo = 0
    hi = pos
    q = 'C'
    skip_b1 = (tr[('B', 1)] == (1, 1, 'B'))
    skip_e1 = (tr[('E', 1)] == (1, -1, 'E'))
    skip_f1 = (tr[('F', 1)] == (1, -1, 'F'))

    if verbose:
        print(f"=== Trace {tm_str} k={k} N={N} ===")
        print(f"  init: {format_tape(tape, lo, hi, h, q)}")

    for iters in range(1, max_iters + 1):
        if q == 'E' and tape.get(h, 0) == 0:
            while lo <= hi and tape.get(lo, 0) == 0: lo += 1
            while hi >= lo and tape.get(hi, 0) == 0: hi -= 1
            if lo <= hi and h == lo - 1:
                # check K
                if tape.get(h+1,0)==1 and tape.get(h+2,0)==0 and tape.get(h+3,0)==0 and tape.get(hi,0)==1 and tape.get(hi-1,0)==0 and tape.get(hi-2,0)==0:
                    p = h + 4
                    runs = []
                    ok = True
                    while p <= hi - 1:
                        ones = 0
                        while p <= hi - 1 and tape.get(p, 0) == 1:
                            ones += 1; p += 1
                        if ones == 0 or ones % 2 != 0 or tape.get(p,0) != 0 or tape.get(p+1,0) != 0:
                            ok = False; break
                        p += 2
                        runs.append(ones // 2)
                    if ok and len(runs) >= 2 and len(runs) - 1 >= max(2, N - 2*k - 3):
                        k_len = len(runs) - 1
                        dL = k_len - N
                        I_par = sum(runs) % 2
                        if verbose:
                            print(f"  [{iters:4d}] CHECK_K MATCH: a={runs[0]}, k_len={k_len}, dL={dL}, I_par={I_par}, runs[:10]={runs[:10]}")
                        return ('K', dL, I_par, runs)

                # check M5 (even_odd tower collapse)
                if tape.get(h+1,0)==1 and tape.get(h+2,0)==0 and tape.get(h+3,0)==0:
                    p = h + 4
                    even_runs = []
                    odd_pos = -1
                    odd_len = -1
                    while p <= hi:
                        ones = 0
                        p_start = p
                        while p <= hi and tape.get(p, 0) == 1:
                            ones += 1; p += 1
                        if ones % 2 == 1:
                            odd_pos = p_start; odd_len = ones; break
                        if p + 1 <= hi and tape.get(p, 0) == 0 and tape.get(p+1, 0) == 0:
                            even_runs.append(ones // 2)
                            p += 2
                        else:
                            break
                    if len(even_runs) >= 1 and odd_pos != -1:
                        s_digits = len(even_runs) - 1
                        d_odd = odd_len // 2
                        first_even_val = even_runs[0]
                        has_nonzero_even = any(x > 0 for x in even_runs[1:])
                        if first_even_val >= 2 and (has_nonzero_even or d_odd >= 1):
                            m0 = 0
                            for x in even_runs[1:]:
                                if x == 0: m0 += 1
                                else: break
                            if 3 * first_even_val + 3 >= m0:
                                total_parity = (sum(even_runs) + d_odd) % 2
                                base_u = 6 * ((s_digits + 10) // 6 + 1)
                                if base_u < 60: base_u = 60
                                if base_u % 12 != 0: base_u += 6
                                u_cap = base_u + 6 * total_parity
                                if verbose:
                                    print(f"  [{iters:4d}] M5 (even_odd): even_runs={even_runs}, odd_len={odd_len} (d_odd={d_odd}), s={s_digits}, par={total_parity} -> u_cap={u_cap}")
                                    print(f"         before: {format_tape(tape, lo, hi, h, q)}")
                                rem_one_pos = odd_pos + 2 * d_odd
                                zeros_span = 2 * s_digits + 2
                                new_h = rem_one_pos - zeros_span - u_cap - 4
                                for idx in range(lo, rem_one_pos):
                                    tape.pop(idx, None)
                                h = new_h
                                tape[h+1] = 1; tape[h+2] = 0; tape[h+3] = 0
                                for idx in range(h+4, h+4+u_cap):
                                    tape[idx] = 1
                                lo = h + 1
                                if verbose:
                                    print(f"         after : {format_tape(tape, lo, hi, h, q)}")
                                continue

            # check Macro 1 / Macro 2
            zeros_left = 10**9 if h < lo else 0
            if h >= lo:
                p_left = h - 1
                while p_left >= lo - 10 and tape.get(p_left, 0) == 0:
                    p_left -= 1
                zeros_left = (h - 1) - p_left if p_left >= lo else 10**9

            if tape.get(h+1,0)==1 and tape.get(h+2,0)==0 and tape.get(h+3,0)==0:
                p = h + 4
                while p <= hi and tape.get(p, 0) == 1: p += 1
                u = p - (h + 4)
                pz = p
                while pz <= hi + 2 and tape.get(pz, 0) == 0: pz += 1
                zeros = pz - p
                if zeros == 2 and tape.get(pz, 0) == 1 and tape.get(pz+1, 0) == 1:
                    pr = pz
                    while pr <= hi and tape.get(pr, 0) == 1: pr += 1
                    r = pr - pz
                    if zeros_left >= 2 * u + 4:
                        u_ll = u
                        r_orig = r
                        while r >= 2 and zeros_left >= 2 * u_ll + 4 and not (h < lo and u_ll >= 60):
                            shift = 2 * u_ll + 4
                            h -= shift
                            zeros_left -= shift
                            u_ll = 3 * u_ll + 6
                            r -= 2
                        if r >= 2 and h < lo and u_ll >= 60:
                            rem_dec = r // 2
                            r = r % 2
                            u_cap = (60 + 6 * (((u_ll // 2) + rem_dec) % 2)) if (u_ll % 2 == 0) else (69 - 6 * ((u_ll // 2) % 2))
                            if verbose:
                                print(f"  [{iters:4d}] M1 COLLAPSE: u_start={u}, r_orig={r_orig}, u_ll={u_ll}, rem_dec={rem_dec} -> u_cap={u_cap}, r_rem={r}")
                            new_h = (pr - r - 2) - u_cap - 4
                            for idx in range(lo, pr - r):
                                tape.pop(idx, None)
                            h = new_h
                            u_ll = u_cap
                            lo = h + 1
                        u = u_ll
                        tape[h] = 0; tape[h+1] = 1; tape[h+2] = 0; tape[h+3] = 0
                        for idx in range(h+4, h+4+u): tape[idx] = 1
                        tape[h+4+u] = 0; tape[h+5+u] = 0
                        for idx in range(h+6+u, pr - r): tape.pop(idx, None)
                        if h + 1 < lo: lo = h + 1
                        continue
                elif zeros >= 4 and zeros % 2 == 0 and tape.get(pz, 0) == 1 and tape.get(pz+1, 0) == 1:
                    m = (zeros // 2) - 1
                    if zeros_left >= 2 * u + 4 and 3 * u + 6 >= 2 * m:
                        shift = 2 * u + 4
                        h -= shift
                        tape[h] = 0; tape[h+1] = 1; tape[h+2] = 0; tape[h+3] = 0
                        pos_w = h + 4
                        for _ in range(m):
                            tape[pos_w] = 1; tape[pos_w+1] = 1; tape[pos_w+2] = 0; tape[pos_w+3] = 0
                            pos_w += 4
                        rem_ones = 3 * u + 6 - 2 * m
                        for _ in range(rem_ones):
                            tape[pos_w] = 1; pos_w += 1
                        tape[pos_w] = 0; tape[pos_w+1] = 0
                        if h + 1 < lo: lo = h + 1
                        continue
            if zeros_left >= 2 and tape.get(h+1, 0) == 1:
                p = h + 1
                while p <= hi and tape.get(p, 0) == 1: p += 1
                m = p - (h + 1)
                if tape.get(p, 0) == 0 and tape.get(p+1, 0) == 0 and tape.get(p+2, 0) == 1:
                    p2 = p + 2
                    while p2 <= hi and tape.get(p2, 0) == 1: p2 += 1
                    n = p2 - (p + 2)
                    c = min(zeros_left // 2, n)
                    if c > 0:
                        h_new = h - 2 * c
                        for idx in range(h_new + 1, h_new + 1 + m + 3 * c):
                            tape[idx] = 1
                        z_pos = h + m + c + 1
                        tape[z_pos] = 0; tape[z_pos+1] = 0
                        h = h_new
                        if h + 1 < lo: lo = h + 1
                        continue

        b = tape.get(h, 0)
        if b == 1:
            if q == 'B' and skip_b1:
                while tape.get(h, 0) == 1: h += 1
                continue
            elif (q == 'E' and skip_e1) or (q == 'F' and skip_f1):
                while tape.get(h, 0) == 1: h -= 1
                continue
        if q in ('H', 'I') or (q == 'C' and b == 1):
            if verbose:
                print(f"  [{iters:4d}] {q}{b}: {format_tape(tape, lo, hi, h, q)}")
        act = tr[(q, b)]
        if act is None:
            if verbose:
                print(f"  [{iters:4d}] HALT at {q}{b}: {format_tape(tape, lo, hi, h, q)}")
            return ('H', q+str(b))
        w, d, nxt = act
        tape[h] = w
        if w == 1:
            if h < lo: lo = h
            if h > hi: hi = h
        h += d
        q = nxt

if __name__ == '__main__':
    tm = "1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_---1RI_1RA0LF"
    for k in range(1, 10):
        trace_machine(tm, k, 2*k+10, verbose=True)
