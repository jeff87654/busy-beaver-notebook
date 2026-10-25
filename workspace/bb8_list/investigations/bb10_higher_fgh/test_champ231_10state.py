import sys, math
from functools import lru_cache

def parse_tm(tm_str):
    parts = tm_str.strip().split('_')
    tr = []
    for p in parts:
        tr.append(p[:3])
        tr.append(p[3:6])
    return tr

def fmt_tm(tr):
    out = []
    for i in range(0, len(tr), 2):
        out.append(tr[i] + tr[i+1])
    return "_".join(out)

def factor(n):
    f = {}; p = 2
    while p * p <= n:
        while n % p == 0:
            f[p] = f.get(p, 0) + 1; n //= p
        p += 1
    if n > 1: f[n] = f.get(n, 0) + 1
    return f

def carmichael(n):
    if n == 1: return 1
    l = 1
    for p, e in factor(n).items():
        t = (1 if e == 1 else (2 if e == 2 else 2 ** (e - 2))) if p == 2 else (p - 1) * p ** (e - 1)
        l = l * t // math.gcd(l, t)
    return l

@lru_cache(maxsize=None)
def R_res(I, m):
    if m == 1: return 0
    if m == 2: return I
    m2 = 2 * m; b = 0; c = m2
    while c % 3 == 0: c //= 3; b += 1
    p3 = 3 ** b
    if c == 1: v_c = 0
    else:
        lam = carmichael(c)
        xr = R_res(1 - I, lam)
        e = (3 * xr + 2) % lam + lam * 50
        v_c = (5 * pow(3, e, c) - 3) % c
    v_p3 = (-3) % p3
    if p3 == 1: val = v_c
    elif c == 1: val = v_p3
    else:
        t = ((v_p3 - v_c) * pow(c, -1, p3)) % p3
        val = v_c + c * t
    return (val // 2) % m

def run_sim(tr, k, N, is_232=False, capx=0, max_iters=25000, snap_in=None, save_snap=False):
    OFFSET = 200000
    SZ = 400000
    MIN_SAFE_H = 2000
    d_const = 58 if is_232 else 56
    if snap_in is None:
        tape = bytearray(SZ)
        left_str = "10"*(2*k-1) + "11001"
        right_str = "100" + "1100"*N + "1"
        full_str = left_str + "1" + right_str
        for i, c in enumerate(full_str):
            if c == '1': tape[OFFSET + i] = 1
        lo = OFFSET; hi = OFFSET + len(full_str) - 1
        h = OFFSET + len(left_str); q = 2; step = 0
        collapsed = False; ack_jumps = 0
    else:
        tape, lo, hi, h, q, step, collapsed, ack_jumps = (
            bytearray(snap_in[0]), snap_in[1], snap_in[2], snap_in[3],
            snap_in[4], snap_in[5], snap_in[6], snap_in[7]
        )

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
                        return ("K*" if collapsed else "K", k_len - N, parity_I, ack_jumps, None)

                if tape[h+1] == 1 and tape[h+2] == 0 and tape[h+3] == 0:
                    pos = h + 4
                    even_vals = []
                    odd_pos = -1; odd_len = -1
                    while pos <= hi:
                        ones = 0; p_start = pos
                        while pos <= hi and tape[pos] == 1: ones += 1; pos += 1
                        if ones % 2 == 1:
                            odd_pos = p_start; odd_len = ones; break
                        if pos + 1 <= hi and tape[pos] == 0 and tape[pos+1] == 0:
                            even_vals.append(ones // 2); pos += 2
                        else: break
                    if len(even_vals) >= 1 and odd_pos != -1:
                        s_digits = len(even_vals) - 1
                        d_odd = odd_len // 2
                        has_nonzero_even_digit = any(x > 0 for x in even_vals[1:])
                        if (s_digits >= 1 and has_nonzero_even_digit and (odd_pos < hi or d_odd >= 1)) or (s_digits == 0 and d_odd >= 1 and (even_vals[0] >= 100 or d_odd >= 6)):
                            collapsed = True; ack_jumps += 1
                            total_parity = (sum(even_vals) + d_odd) % 2
                            base_u = max(60, 6 * ((s_digits + 10) // 6 + 1)) + capx
                            if base_u % 12 != 0: base_u += 6
                            u_cap = base_u + 6 * total_parity
                            rem_one_pos = odd_pos + 2 * d_odd
                            zeros_span = 2 * s_digits + 2
                            new_h = rem_one_pos - zeros_span - u_cap - 4
                            tape[lo : rem_one_pos] = b'\x00' * (rem_one_pos - lo)
                            h = new_h
                            tape[h+1] = 1; tape[h+2] = 0; tape[h+3] = 0
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
                        while r >= 2 and zeros_left >= 2 * u + 4 and h - (2 * u + 4) >= MIN_SAFE_H:
                            shift = 2 * u + 4
                            step += 3 * u * u + 33 * u + d_const
                            h -= shift; zeros_left -= shift
                            u = 3 * u + 6; r -= 2
                        if r >= 2 and h < lo and h - (2 * u + 4) < MIN_SAFE_H:
                            collapsed = True; ack_jumps += 1
                            rem_dec = r // 2; r = r % 2
                            u_cap = ((60 + capx) + 6 * (((u // 2) + rem_dec) % 2)) if (u % 2 == 0) else (63 + capx)
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
            snap_out = (tape, lo, hi, h, q, step, collapsed, ack_jumps) if save_snap else None
            return ("H*" if collapsed else "H", f"{chr(65+q)}{b}", slot, ack_jumps, snap_out)
        tape[h] = 1 if act[0] == '1' else 0
        h += 1 if act[1] == 'R' else -1
        q = ord(act[2]) - 65
        step += 1
        if h - 2 < lo: lo = h - 2
        if h + 2 > hi: hi = h + 2
    return ("T", 0, 0, ack_jumps, None)

PARENTS = [
    ("P2_---0RI_1RF1LG (E3)",   "1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_---0RI_1RF1LG", 21),
    ("P2_0RB0RI_0LG--- (E3)",   "1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_0RB0RI_0LG---", 21),
    ("P2_1RD0RI_1LH--- (E3)",   "1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_1RD0RI_1LH---", 21),
    ("CS3_0LE0LI_0LA--- (E3)",  "1RB0RG_1RC1RB_0RD1LD_0LE0LH_0LF1LE_1RA1LF_0LD0RB_0LE0LI_0LA---", 18),
    ("P3_1LG0LI_1LH--- (P3)",   "1RB0RG_1RC1RB_0RD0LH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_1LG0LI_1LH---", 21),
    ("P5_---0LI_1LG0LH (P5)",   "1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_---0LI_1LG0LH", 21),
    ("CASCADE_---1LI_1RB1LH",   "1RB0RG_1RC1RB_0RD0LH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_---1LI_1RB1LH", 20),
    ("CAP_1RI_1RA0LF",          "1RB0RG_1RC1RB_0RD1RH_0LE0LD_0LF1LE_1RA1LF_0LD0RB_---1RI_1RA0LF", 21),
]

def solve_traj(cls, kmax=35, k1=20, I1=1, max_rounds=30):
    if cls[k1][0] == 'H':
        return ('HALT', 1, [])
    if cls[k1][0] != 'K':
        return ('R1_' + cls[k1][0], 1, [])
    # Fit periodic or affine model on k = 14..kmax
    for P in range(1, 15):
        for k0 in range(14, kmax - 3 * P + 1):
            ok = True; model = {}
            for s0 in range(k0, k0 + P):
                ks = list(range(s0, kmax + 1, P))
                if len(ks) < 3: ok = False; break
                kinds = {cls[k][0] for k in ks}
                if len(kinds) != 1: ok = False; break
                kd = kinds.pop()
                if kd == 'H':
                    model[s0 % P] = ('H', s0); continue
                if kd != 'K': ok = False; break
                dls = [cls[k][1] for k in ks]
                Is = [cls[k][2] for k in ks]
                c = dls[1] - dls[0]
                if any(dls[i+1] - dls[i] != c for i in range(len(dls)-1)): ok = False; break
                e = (Is[1] - Is[0]) % 2
                if any((Is[i+1] - Is[i]) % 2 != e for i in range(len(Is)-1)): ok = False; break
                model[s0 % P] = ('K', s0, dls[0], c, Is[0], e)
            if ok:
                D = 12
                M0 = (2**6) * (3**4) * (5**2) * 7
                L = (P ** D) * M0
                _, dL, Iev = cls[k1]
                A = R_res(I1, L)
                N = 3 * A + 1 - k1
                k = (N + dL) % L
                I = (Iev + N) % 2
                traj = [(1, k1 % P, I1, 'K')]
                for r in range(2, D):
                    s = k % P
                    m = model[s]
                    traj.append((r, s, I, m[0]))
                    if m[0] == 'H':
                        return ('HALT', r, traj)
                    _, s0, dl0, c, i0, e = m
                    Ln = L // P
                    t = ((k - s0) // P) % Ln
                    dLk = (dl0 + c * t) % Ln
                    Ik = (i0 + e * t) % 2
                    A = R_res(I, Ln)
                    N = (3 * A + 1 - k) % Ln
                    k = (N + dLk) % Ln
                    I = (Ik + N) % 2
                    L = Ln
                return (f'ALIVE>={D}', D, traj)
    return ('NOFIT', 1, [])

if __name__ == "__main__":
  for label, tm9, k_halt in PARENTS:
    tr9 = parse_tm(tm9)
    is_232 = "_1LC0RB_" in tm9
    # Precompute parent table and snapshots for k = 12..35
    parent_n1 = {}
    parent_n2 = {}
    parent_c12 = {}
    for k in range(12, 36):
        parent_n1[k] = run_sim(tr9, k, 2*k + 10, is_232=is_232, capx=0, save_snap=True)
        if parent_n1[k][0] in ("K", "K*"):
            parent_n2[k] = run_sim(tr9, k, 2*k + 20, is_232=is_232, capx=0, save_snap=False)
            parent_c12[k] = run_sim(tr9, k, 2*k + 10, is_232=is_232, capx=12, save_snap=False)
        else:
            parent_n2[k] = run_sim(tr9, k, 2*k + 20, is_232=is_232, capx=0, save_snap=True)
            parent_c12[k] = run_sim(tr9, k, 2*k + 10, is_232=is_232, capx=12, save_snap=True)

    kd0, slot_name, h_slot, c0, snap0 = parent_n1[k_halt]
    print(f"\n=======================================================")
    print(f"PARENT: {label} | {tm9} | k_halt={k_halt} -> {kd0} at {slot_name} (c={c0})")
    if snap0 is None:
        continue
    tape0, lo0, hi0, h0, q0, step0, col0, aj0 = snap0
    k_rebuilders = []
    h_delayed = []
    for hw in ['0', '1']:
        for hd, step_d in [('L', -1), ('R', 1)]:
            h_act = f"{hw}{hd}J"
            c1 = tape0[h0 + step_d]
            j_slot1 = 2 * 9 + c1
            for jw in ['0', '1']:
                for jd in ['L', 'R']:
                    for jnx_idx in range(10):
                        j_act = f"{jw}{jd}{chr(65 + jnx_idx)}"
                        tr10 = list(tr9) + ["---", "---"]
                        tr10[h_slot] = h_act
                        tr10[j_slot1] = j_act
                        kd, dL, I, c, _ = run_sim(tr10, k_halt, 2*k_halt + 10, is_232=is_232, snap_in=snap0)
                        if kd in ("K", "K*"):
                            k_rebuilders.append((h_act, j_slot1, j_act, tr10, kd, dL, I, c))
                        elif kd in ("H", "H*") and c > c0:
                            h_delayed.append((h_act, j_slot1, j_act, tr10, kd, dL, c))
    print(f"  160 lazy-TNF J-extensions on k={k_halt}: K-rebuilders={len(k_rebuilders)}, delayed-H (c>{c0})={len(h_delayed)}")
    for h_act, j_slot1, j_act, tr10, kd, slot_h, c in sorted(h_delayed, key=lambda x: -x[6])[:6]:
        print(f"    [Delayed H] {slot_name}={h_act} J{j_slot1-18}={j_act} -> {kd} at {slot_h} with c={c} (was {c0})")
    for h_act, j_slot1, j_act, tr10, kd, dL, I, c in k_rebuilders:
        ks_res = {}
        any_h = []
        rob_ok = True
        for k in range(12, 36):
            p1 = parent_n1[k]
            if p1[0] in ("K", "K*"):
                r_n1, r_n2, r_c12 = p1, parent_n2[k], parent_c12[k]
            else:
                r_n1 = run_sim(tr10, k, 2*k + 10, is_232=is_232, capx=0, snap_in=p1[4])
                r_n2 = run_sim(tr10, k, 2*k + 20, is_232=is_232, capx=0, snap_in=parent_n2[k][4]) if parent_n2[k][4] else p1
                r_c12 = run_sim(tr10, k, 2*k + 10, is_232=is_232, capx=12, snap_in=parent_c12[k][4]) if parent_c12[k][4] else p1
            if r_n1[0] in ("H", "H*") and r_n2[0] in ("H", "H*"):
                if r_c12[0] not in ("H", "H*"): rob_ok = False
                any_h.append(k)
                ks_res[k] = ("H", 0, 0)
            elif r_n1[0] in ("K", "K*") and r_n2[0] in ("K", "K*") and r_n1[1] == r_n2[1] and r_n1[2] == r_n2[2]:
                if r_c12[0] not in ("K", "K*") or r_c12[1] != r_n1[1] or r_c12[2] != r_n1[2]:
                    rob_ok = False
                ks_res[k] = ("K", r_n1[1], r_n1[2])
            else:
                ks_res[k] = ("X", r_n1[0], r_n2[0])
        res_s, r_s, traj_s = solve_traj(ks_res, kmax=35)
        if any_h or res_s.startswith("HALT"):
            print(f"    [Mixed K+H] {slot_name}={h_act} J{j_slot1-18}={j_act} | solve={res_s} R={r_s} rob={rob_ok} | H_ks={any_h} | traj={traj_s}")
        else:
            x_cnt = sum(1 for v in ks_res.values() if v[0] == "X")
            if x_cnt == 0:
                print(f"    [All-K k=12..35] {slot_name}={h_act} J{j_slot1-18}={j_act} | solve={res_s} rob={rob_ok} | k={k_halt}: dL={dL} I={I} c={c}")
