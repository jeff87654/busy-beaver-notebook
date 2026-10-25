import sys
sys.path.append(r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_beat_h003")
from solve_rounds import R
from trace_all_33 import parse_tm as parse_tm9
from inspect_post_m5_2 import full_blocks

def check_K(tape, lo, hi, h, N):
    if tape.get(h+1,0)!=1 or tape.get(h+2,0)!=0 or tape.get(h+3,0)!=0 or tape.get(hi,0)!=1 or tape.get(hi-1,0)!=0 or tape.get(hi-2,0)!=0:
        return False, 0, 0, 0
    p = h + 4; runs = []
    while p <= hi - 1:
        ones = 0
        while p <= hi - 1 and tape.get(p, 0) == 1: ones += 1; p += 1
        if ones % 2 != 0 or tape.get(p,0) != 0 or tape.get(p+1,0) != 0: return False, 0, 0, 0
        p += 2; runs.append(ones // 2)
    if len(runs) < 2: return False, 0, 0, 0
    return True, len(runs) - 1 - N, sum(runs) % 2, runs[-1]

def trace_compact(tm_str, k, N, CAPX=0, max_iters=80000):
    tr = parse_tm9(tm_str)
    tape = {}
    pos = 0; lo = 0
    for _ in range(2 * k - 1):
        tape[pos] = 1; tape[pos+1] = 0; pos += 2
    for b in [1, 1, 0, 0, 1]:
        tape[pos] = b; pos += 1
    h = pos
    for b in [1, 1, 0, 0]:
        tape[pos] = b; pos += 1
    for _ in range(N):
        for b in [1, 1, 0, 0]:
            tape[pos] = b; pos += 1
    tape[pos] = 1; hi = pos
    q = 'C'; iters = 0; collapsed = False; clears = 0
    skip_b1 = (tr[('B', 1)] == (1, 1, 'B'))
    skip_e1 = (tr[('E', 1)] == (1, -1, 'E'))
    skip_f1 = (tr[('F', 1)] == (1, -1, 'F'))

    print(f"\n=== {tm_str} k={k}, N={N}, CAPX={CAPX} ===")
    while iters < max_iters:
        iters += 1
        if q == 'E' and tape.get(h, 0) == 0:
            while lo <= hi and tape.get(lo, 0) == 0: lo += 1
            while hi >= lo and tape.get(hi, 0) == 0: hi -= 1
            if lo <= hi and h == lo - 1:
                ok, dL, I_par, d_last = check_K(tape, lo, hi, h, N)
                if ok:
                    min_valid = max(2, N - 2 * k - 3)
                    if dL + N >= min_valid:
                        print(f"  [{iters:5d}] CHECK_K (dL={dL}, I={I_par}, clears={clears}): {full_blocks(tape, lo, hi, h, q)}")
                        return ('K', dL, I_par, clears)
                if h + 4 <= hi and tape.get(h+1, 0) == 1 and tape.get(h+2, 0) == 0 and tape.get(h+3, 0) == 0:
                    p = h + 4; even_count = 0; first_even_val = 0; odd_pos = -1; odd_len = -1
                    has_nz = False; sum_even = 0
                    while p <= hi:
                        ones = 0; p_start = p
                        while p <= hi and tape.get(p, 0) == 1: ones += 1; p += 1
                        if ones % 2 == 1: odd_pos = p_start; odd_len = ones; break
                        if p + 1 <= hi and tape.get(p, 0) == 0 and tape.get(p+1, 0) == 0:
                            val = ones // 2
                            if even_count == 0: first_even_val = val
                            elif val > 0: has_nz = True
                            sum_even += val; even_count += 1; p += 2
                        else: break
                    if even_count >= 1 and odd_pos != -1:
                        s_digits = even_count - 1; d_odd = odd_len // 2
                        if first_even_val >= 2 and (has_nz or d_odd >= 1):
                            m0 = 0; p_scan = h + 4 + 2 * first_even_val + 2
                            while m0 < s_digits and tape.get(p_scan, 0) == 0 and tape.get(p_scan+1, 0) == 0:
                                m0 += 1; p_scan += 2
                            if 3 * first_even_val + 3 >= m0:
                                collapsed = True; clears += 1
                                total_parity = (sum_even + d_odd) % 2
                                base_u = 6 * ((s_digits + 10) // 6 + 1)
                                if base_u < 60: base_u = 60
                                if base_u % 12 != 0: base_u += 6
                                u_cap = base_u + 6 * total_parity + CAPX
                                rem_one_pos = odd_pos + 2 * d_odd
                                zeros_span = 2 * s_digits + 2
                                new_h = rem_one_pos - zeros_span - u_cap - 4
                                print(f"  [{iters:5d}] M5 #{clears} (s={s_digits}, d_odd={d_odd}, par={total_parity} -> u_cap={u_cap})")
                                for idx in range(lo, rem_one_pos): tape.pop(idx, None)
                                h = new_h; tape[h+1] = 1; tape[h+2] = 0; tape[h+3] = 0
                                for idx in range(h+4, h+4+u_cap): tape[idx] = 1
                                lo = h + 1
                                continue
            if h < lo: zeros_left = 100000
            else:
                p_left = h - 1
                while p_left >= lo - 10 and tape.get(p_left, 0) == 0: p_left -= 1
                zeros_left = (h - 1) - p_left if p_left >= lo else 100000
            if h + 4 <= hi and tape.get(h+1, 0) == 1 and tape.get(h+2, 0) == 0 and tape.get(h+3, 0) == 0:
                p = h + 4
                while p <= hi and tape.get(p, 0) == 1: p += 1
                u = p - (h + 4); pz = p
                while pz <= hi + 2 and tape.get(pz, 0) == 0: pz += 1
                zeros = pz - p
                if zeros == 2 and pz + 1 <= hi and tape.get(pz, 0) == 1 and tape.get(pz+1, 0) == 1:
                    pr = pz
                    while pr <= hi and tape.get(pr, 0) == 1: pr += 1
                    r = pr - pz; r_orig = r
                    if zeros_left >= 2 * u + 4:
                        u_ll = u
                        while r >= 2 and zeros_left >= 2 * u_ll + 4 and not (h < lo and u_ll >= 60 + CAPX):
                            shift = 2 * u_ll + 4; h -= shift; zeros_left -= shift
                            u_ll = 3 * u_ll + 6; r -= 2
                        if r >= 2 and h < lo and u_ll >= 60 + CAPX:
                            collapsed = True; clears += 1
                            rem_dec = r // 2; r = r % 2
                            if u_ll % 2 == 0:
                                u_cap = 60 + CAPX + 6 * (((u_ll // 2) + rem_dec) % 2)
                            else:
                                u_cap = 69 + CAPX - 6 * ((u_ll // 2) % 2)
                            if clears <= 10 or r_orig < 150 or clears % 50 == 0:
                                print(f"  [{iters:5d}] M1 #{clears} (u_start={u}, r_orig={r_orig}, u_ll={u_ll}, rem_dec={rem_dec} -> u_cap={u_cap}, r_rem={r})")
                            new_h = (pr - r - 2) - u_cap - 4
                            for idx in range(lo, pr - r): tape.pop(idx, None)
                            h = new_h; u_ll = u_cap; lo = h + 1
                        u = u_ll
                        tape[h] = 0; tape[h+1] = 1; tape[h+2] = 0; tape[h+3] = 0
                        for idx in range(h+4, h+4+u): tape[idx] = 1
                        tape[h+4+u] = 0; tape[h+5+u] = 0
                        for idx in range(h+6+u, pr - r): tape.pop(idx, None)
                        if h + 1 < lo: lo = h + 1
                        if collapsed and (clears <= 10 or r_orig < 150 or clears % 50 == 0):
                            print(f"          after M1: {full_blocks(tape, lo, hi, h, q)}")
                        continue
                elif zeros >= 4 and zeros % 2 == 0 and tape.get(pz, 0) == 1 and tape.get(pz+1, 0) == 1:
                    m = (zeros // 2) - 1
                    if zeros_left >= 2 * u + 4 and 3 * u + 6 >= 2 * m:
                        shift = 2 * u + 4; h -= shift
                        tape[h] = 0; tape[h+1] = 1; tape[h+2] = 0; tape[h+3] = 0
                        pos_w = h + 4
                        for _ in range(m):
                            tape[pos_w] = 1; tape[pos_w+1] = 1; tape[pos_w+2] = 0; tape[pos_w+3] = 0; pos_w += 4
                        rem_ones = 3 * u + 6 - 2 * m
                        for _ in range(rem_ones): tape[pos_w] = 1; pos_w += 1
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
                        for idx in range(h_new + 1, h_new + 1 + m + 3 * c): tape[idx] = 1
                        z_pos = h + m + c + 1; tape[z_pos] = 0; tape[z_pos+1] = 0; h = h_new
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
        act = tr[(q, b)]
        if act is None:
            print(f"  [{iters:5d}] HALT at {q}{b} (clears={clears})")
            return ('H', 0, 0, clears)
        w, d, nxt = act
        tape[h] = w
        if w == 1:
            if h < lo: lo = h
            if h > hi: hi = h
        h += d; q = nxt
    print(f"  [{iters:5d}] TIMEOUT (clears={clears})")
    return ('T', 0, 0, clears)

if __name__ == '__main__':
    g7 = "1RB0RG_1RC1RB_0RD0RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_1LD0LI_1LH---"
    for k in range(5, 19):
        trace_compact(g7, k, 2 * k + 10, 0)
        trace_compact(g7, k, 2 * k + 11, 0)
    print("\n=== G7_1LD0LI Round Trajectory from k1=20, I1=1 ===")
    Q = 14
    for I in [0, 1]:
        print(f"R({I}, {Q}) = {R(I, Q)}")
    k = 20; I = 1
    for r in range(1, 15):
        mod7 = k % 7
        print(f"Round {r}: k mod 14 = {k % 14} (k mod 7 = {mod7}), I = {I}")
        if mod7 == 0:
            print("  -> HALT (H)")
            break
        elif mod7 in (2, 3):
            print("  -> LIST-COLLAPSING (C)")
            break
        elif mod7 in (1, 4):
            dL, Iev = -1, 0
        else: # mod7 in (5, 6)
            dL, Iev = 1, 1
        A = R(I, Q)
        N = 3 * A + 1 - k
        k = (N + dL) % Q
        I = (Iev + N) % 2
