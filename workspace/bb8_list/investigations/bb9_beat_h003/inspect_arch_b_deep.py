import sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts')
import idle
from test_arch_b import parse_tr, sim_from_blocks

def sim_r4_end_exact(M, K_twos=25, max_iters=50000):
    is_232 = '1LC0RB' in M
    tr = parse_tr(M)
    OFFSET = 300000
    SZ = 600000
    tape = bytearray(SZ)
    init_blocks = [13, 1] + [2]*K_twos
    pos = OFFSET
    h = pos
    tape[pos+1] = 1; tape[pos+2] = 0; tape[pos+3] = 0
    p = pos + 4
    for b in init_blocks:
        for _ in range(b):
            tape[p] = 1
            p += 1
        tape[p] = 0; tape[p+1] = 0
        p += 2
    tape[p] = 1
    lo = pos + 1
    hi = p
    q = 4
    step = 0
    MIN_SAFE_H = 2000
    d_const = 58 if is_232 else 56
    ack_jumps = 0
    h0_entries = 0
    i_entries = 0

    for iters in range(1, max_iters + 1):
        if q == 4 and tape[h] == 0:
            while lo <= hi and tape[lo] == 0: lo += 1
            while hi >= lo and tape[hi] == 0: hi -= 1
            if lo <= hi and h == lo - 1 and h + 4 <= hi:
                if tape[h+1] == 1 and tape[h+2] == 0 and tape[h+3] == 0 and tape[hi] == 1 and tape[hi-1] == 0 and tape[hi-2] == 0:
                    pos = h + 4; ok = True; blocks = []
                    while pos <= hi - 1:
                        ones = 0
                        while pos <= hi - 1 and tape[pos] == 1: ones += 1; pos += 1
                        if pos + 1 > hi - 1 or tape[pos] != 0 or tape[pos+1] != 0: ok = False; break
                        pos += 2; blocks.append(ones)
                    if ok and len(blocks) >= 2:
                        odds = [(idx, val) for idx, val in enumerate(blocks) if val % 2 == 1]
                        if not odds and blocks[0] >= 2 and (h0_entries > 0 or i_entries > 0):
                            # All blocks are even! This is a 100% CLEAN K configuration!
                            twos_tail = 0
                            for x in reversed(blocks):
                                if x == 2: twos_tail += 1
                                else: break
                            return ('CLEAN_K_START_R5', len(blocks), twos_tail, blocks[:-twos_tail] if twos_tail else blocks, ack_jumps, h0_entries, i_entries, iters)

                # Macro 5 & Macro 4, EXCEPT we do NOT allow Macro 4 to treat the final sentinel `hi` (ones=1 at pos==hi+1) as an odd block!
                if tape[h+1] == 1 and tape[h+2] == 0 and tape[h+3] == 0:
                    p0 = h + 4
                    while p0 <= hi and tape[p0] == 1: p0 += 1
                    u0 = p0 - (h + 4)
                    if u0 % 2 == 1 and p0 + 1 <= hi and tape[p0] == 0 and tape[p0+1] == 0:
                        pos = p0 + 2
                        s_digits = 0
                        has_nz = False
                        while pos <= hi - 1:
                            ones = 0; p_start = pos
                            while pos <= hi - 1 and tape[pos] == 1: ones += 1; pos += 1
                            if ones % 2 == 0 and pos + 1 <= hi - 1 and tape[pos] == 0 and tape[pos+1] == 0:
                                if ones > 0: has_nz = True
                                s_digits += 1; pos += 2
                            else:
                                pos = p_start; break
                        if s_digits >= 1 and has_nz and 3 * u0 + 6 >= 2 * s_digits:
                            ack_jumps += 1
                            base_u = max(60, 6 * ((s_digits + 10) // 6 + 1))
                            if base_u % 12 != 0: base_u += 6
                            u_cap = base_u + 3
                            zeros_span = 2 * s_digits + 2
                            new_h = pos - zeros_span - u_cap - 4
                            tape[lo : pos] = b'\x00' * (pos - lo)
                            h = new_h
                            tape[h+1] = 1; tape[h+2] = 0; tape[h+3] = 0
                            tape[h+4 : h+4+u_cap] = b'\x01' * u_cap
                            lo = h + 1; step += 1000000000
                            continue

                    pos = h + 4; even_vals = []; odd_pos = -1; odd_len = -1
                    while pos <= hi - 1:
                        ones = 0; p_start = pos
                        while pos <= hi - 1 and tape[pos] == 1: ones += 1; pos += 1
                        if ones % 2 == 1:
                            if pos + 1 <= hi - 1 and tape[pos] == 0 and tape[pos+1] == 0:
                                odd_pos = p_start; odd_len = ones
                            break
                        if pos + 1 <= hi - 1 and tape[pos] == 0 and tape[pos+1] == 0:
                            even_vals.append(ones // 2); pos += 2
                        else: break
                    if len(even_vals) >= 1 and odd_pos != -1:
                        s_digits = len(even_vals) - 1
                        d_odd = odd_len // 2
                        has_nz = any(x > 0 for x in even_vals[1:])
                        m0 = 0
                        while m0 < s_digits and even_vals[1 + m0] == 0: m0 += 1
                        if even_vals[0] >= 2 and 3 * even_vals[0] + 3 >= m0 and (has_nz or d_odd >= 1):
                            ack_jumps += 1
                            total_parity = (sum(even_vals) + d_odd) % 2
                            base_u = max(60, 6 * ((s_digits + 10) // 6 + 1))
                            if base_u % 12 != 0: base_u += 6
                            u_cap = base_u + 6 * total_parity
                            rem_one_pos = odd_pos + 2 * d_odd
                            zeros_span = 2 * s_digits + 2
                            new_h = rem_one_pos - zeros_span - u_cap - 4
                            tape[lo : rem_one_pos] = b'\x00' * (rem_one_pos - lo)
                            h = new_h
                            tape[h+1] = 1; tape[h+2] = 0; tape[h+3] == 0
                            tape[h+4 : h+4+u_cap] = b'\x01' * u_cap
                            lo = h + 1; step += 1000000000
                            continue

            if h < lo: zeros_left = h - MIN_SAFE_H
            else:
                p_left = h - 1
                while tape[p_left] == 0: p_left -= 1
                zeros_left = h - 1 - p_left

            if tape[h+1] == 1 and tape[h+2] == 0 and tape[h+3] == 0:
                p = h + 4
                while tape[p] == 1: p += 1
                u = p - (h + 4); pz = p
                while pz <= hi + 2 and tape[pz] == 0: pz += 1
                zeros = pz - p
                if zeros == 2 and tape[pz] == 1 and tape[pz+1] == 1:
                    pr = pz
                    while tape[pr] == 1: pr += 1
                    r = pr - pz
                    if zeros_left >= 2 * u + 4 and h - (2 * u + 4) >= MIN_SAFE_H:
                        while r >= 2 and zeros_left >= 2 * u + 4 and h - (2 * u + 4) >= MIN_SAFE_H and not (h < lo and u >= 60):
                            shift = 2 * u + 4
                            step += 3 * u * u + 33 * u + d_const
                            h -= shift; zeros_left -= shift; u = 3 * u + 6; r -= 2
                        if r >= 2 and h < lo and (u >= 60 or h - (2 * u + 4) < MIN_SAFE_H):
                            ack_jumps += 1
                            rem_dec = r // 2; r = r % 2
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
                        pos += rem_ones; tape[pos] = 0; tape[pos+1] = 0
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
                        tape[h_new + 1 : h_new + 1 + m + 3 * c] = b'\x01' * (m + 3 * c)
                        tape[h + m + c + 1] = 0; tape[h + m + c + 2] = 0
                        h = h_new
                        if h + 1 < lo: lo = h + 1
                        if h + m + c + 2 > hi: hi = h + m + c + 2
                        step += c * (2 * m + 10) + 3 * c * (c - 1)
                        continue

        b = tape[h]
        if b == 1:
            if q == 1:
                p = h + 1
                while tape[p] == 1: p += 1
                step += (p - h); h = p
                if h + 2 > hi: hi = h + 2
                continue
            elif q == 4 or q == 5:
                p = h - 1
                while tape[p] == 1: p -= 1
                step += (h - p); h = p
                if h - 2 < lo: lo = h - 2
                continue

        if q == 7 and b == 0: h0_entries += 1
        if q == 8: i_entries += 1
        act = tr[2 * q + b]
        if act[0] == -1:
            return ('HALT', f'{chr(65+q)}{b}', step, ack_jumps, h0_entries, i_entries, iters)
        tape[h] = act[0]
        if act[0] == 1:
            if h < lo: lo = h
            if h > hi: hi = h
        h += act[1]
        q = act[2]
        step += 1
        if h < MIN_SAFE_H or h >= SZ - MIN_SAFE_H:
            return ('OOB', h - OFFSET, step, ack_jumps, h0_entries, i_entries, iters)
    return ('MAX_ITERS', step, ack_jumps, h0_entries, i_entries)

print("=== Exact CLEAN_K_START_R5 check on 8-state H0 choices from [13, 1, 2^25] ===")
for w in '01':
    for d in 'LR':
        for s in 'ABCDEFGH':
            h0 = f'{w}{d}{s}'
            M = f'1RB0RG_1RC1RB_0RD0RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_{h0}1RG'
            res = sim_r4_end_exact(M, K_twos=25, max_iters=30000)
            if res[0] == 'CLEAN_K_START_R5':
                print(f'  H0={h0}: {res}')
