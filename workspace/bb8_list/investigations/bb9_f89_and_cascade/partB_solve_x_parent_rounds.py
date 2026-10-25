import os, re, math, subprocess
from collections import Counter, defaultdict
from functools import lru_cache

WORKDIR = r"C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_f89_and_cascade"
OUT_TXT = os.path.join(WORKDIR, "partB_screen_x_parents.out.txt")

with open(OUT_TXT, "r") as f:
    lines = [line.strip() for line in f if line.startswith("[MIXED")]

def parse_tm(tm_str):
    parts = tm_str.split("_")
    T = []
    for p in parts:
        for b in (0, 1):
            s = p[3*b:3*b+3]
            if s == "---":
                T.append((-1, 0, -1))
            else:
                T.append((int(s[0]), 1 if s[1] == 'R' else -1, ord(s[2]) - ord('A')))
    return T

def test_kc_preservation(tm_str):
    """Simulate from Kc([1, 1], 1, 1) literally, jumping R1ITER when a >= 2, until ds == (0, 0), a == 0."""
    T = parse_tm(tm_str)
    tape = defaultdict(int)
    seq = [0] + [1]*3 + [0,0] + [1]*2 + [0,0] + [1]*2 + [0,0] + [1]*2 + [0,0] + [1]
    for idx, val in enumerate(seq):
        tape[idx] = val
    pos = 0; q = 4; lo = 0; hi = len(seq) - 1
    for step in range(1, 30000):
        c = tape[pos]
        if q == 4 and c == 0 and step > 1:
            if tape[pos+1] == 1 and all(tape[i] == 0 for i in range(lo, pos)):
                r1 = hi
                while r1 > pos and tape[r1] == 0: r1 -= 1
                i = pos + 1; ones = 0
                while i <= r1 and tape[i] == 1: ones += 1; i += 1
                if ones % 2 == 1 and i + 1 <= r1 and tape[i] == 0 and tape[i+1] == 0:
                    b = (ones - 1) // 2; i += 2; fld = []; ok = True
                    while True:
                        o = 0
                        while i <= r1 and tape[i] == 1: o += 1; i += 1
                        if i > r1:
                            if o == 1: break
                            ok = False; break
                        if o % 2 == 1 or tape[i] != 0 or i + 1 > r1 or tape[i+1] != 0:
                            ok = False; break
                        fld.append(o // 2); i += 2
                    if ok and len(fld) >= 1:
                        a = fld[0]; ds = tuple(fld[1:])
                        if ds == (21, 0):
                            # R1ITER, B_0 borrow, and B_1 borrow all succeeded!
                            return True, f"OK(a={a},b={b},step={step})"
        w, d, nx = T[2*q + c]
        if nx < 0:
            return False, f"HALT({chr(65+q)}{c},step={step})"
        tape[pos] = w; pos += d
        if pos < lo: lo = pos
        if pos > hi: hi = pos
        q = nx
    return False, "TIMEOUT"

# Simulate exhaustion gadget on (10)^(2k-1) [C1] 1 00 (1100)^N 1 for any k and N
def sim_exhaustion(T, k, N, max_steps=15000):
    tape = defaultdict(int)
    idx = 0
    for _ in range(2*k - 1):
        tape[idx] = 1; tape[idx+1] = 0; idx += 2
    c_pos = idx
    tape[idx] = 1; tape[idx+1] = 0; tape[idx+2] = 0; idx += 3
    for _ in range(N):
        tape[idx] = 1; tape[idx+1] = 1; tape[idx+2] = 0; tape[idx+3] = 0; idx += 4
    tape[idx] = 1
    lo, hi = 0, idx
    pos = c_pos; q = 2 # C
    for step in range(1, max_steps + 1):
        c = tape[pos]
        w, d, nx = T[2*q + c]
        if nx < 0:
            return ('H', 0, 0, step)
        tape[pos] = w; pos += d
        if pos < lo: lo = pos
        if pos > hi: hi = pos
        q = nx
        if q == 4 and tape[pos] == 0 and tape[pos+1] == 1:
            if all(tape[i] == 0 for i in range(lo, pos)):
                r1 = hi
                while r1 > pos and tape[r1] == 0: r1 -= 1
                i = pos + 1; ones = 0
                while i <= r1 and tape[i] == 1: ones += 1; i += 1
                if ones % 2 == 1 and i + 1 <= r1 and tape[i] == 0 and tape[i+1] == 0:
                    b = (ones - 1) // 2; i += 2; fld = []; ok = True
                    while True:
                        o = 0
                        while i <= r1 and tape[i] == 1: o += 1; i += 1
                        if i > r1:
                            if o == 1: break
                            ok = False; break
                        if o % 2 == 1 or tape[i] != 0 or i + 1 > r1 or tape[i+1] != 0:
                            ok = False; break
                        fld.append(o // 2); i += 2
                    if ok and len(fld) >= 2:
                        a = fld[0]; ds = fld[1:]
                        # Check if first non-zero digit is within b+3a
                        mz = 0
                        while mz < len(ds) and ds[mz] == 0: mz += 1
                        if mz < len(ds) and mz <= b + 3*a:
                            dL = len(ds) - N
                            I_par = (a + b + sum(ds)) % 2
                            return ('K', dL, I_par, step)
    return ('T', 0, 0, max_steps)

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
        t = (1 if e == 1 else (2 if e == 2 else 2**(e-2))) if p == 2 else (p - 1) * p**(e - 1)
        l = l * t // math.gcd(l, t)
    return l

@lru_cache(maxsize=None)
def R_tower(I, m):
    if m == 1: return 0
    if m == 2: return I
    m2 = 2 * m; b = 0; c = m2
    while c % 3 == 0: c //= 3; b += 1
    p3 = 3 ** b
    if c == 1: v_c = 0
    else:
        lam = carmichael(c)
        xr = R_tower(1 - I, lam)
        e = (3 * xr + 2) % lam + lam * 50
        v_c = (5 * pow(3, e, c) - 3) % c
    v_p3 = (-3) % p3
    if p3 == 1: val = v_c
    elif c == 1: val = v_p3
    else:
        t = ((v_p3 - v_c) * pow(c, -1, p3)) % p3
        val = v_c + c * t
    return (val // 2) % m

# Build full k=1..28 tables for each unique (cat, cdesc, res) profile and solve rounds for k1=1, 2, 4!
by_mech = defaultdict(list)
for line in lines:
    m = re.match(r"\[MIXED (\S+) (\S+) (\S+) k1=(\d+)\] (\S+) \| (.*)", line)
    if not m:
        m = re.match(r"\[MIXED (\S+) (\S+) k1=(\d+)\] (\S+) \| (.*)", line)
        cat, pname, k1, tm, res = m.group(1), m.group(2), int(m.group(3)), m.group(4), m.group(5)
        cdesc = "NONE"
    else:
        cat, pname, cdesc, k1, tm, res = m.group(1), m.group(2), m.group(3), int(m.group(4)), m.group(5), m.group(6)
    by_mech[(cat, cdesc, res)].append((pname, k1, tm))

print(f"Testing {len(by_mech)} distinct profiles...")
halters = []
stats = Counter()

for (cat, cdesc, res), items in sorted(by_mech.items()):
    ex_tm = items[0][2]
    kc_ok, kc_msg = test_kc_preservation(ex_tm)
    if not kc_ok:
        stats[f"BAD_KC_{kc_msg}"] += len(items)
        continue
    T = parse_tm(ex_tm)
    # Build table for k = 1..28 at N1=20, N2=40 (both even)
    tab = {}
    for k in range(1, 29):
        r1 = sim_exhaustion(T, k, 20)
        r2 = sim_exhaustion(T, k, 40)
        if r1[0] == 'H' and r2[0] == 'H':
            tab[k] = ('H',)
        elif r1[0] == 'K' and r2[0] == 'K':
            if r1[1] == r2[1] and r1[2] == r2[2]:
                tab[k] = ('K', r1[1], r1[2]) # positional f_omega round: k_{r+1} = N_r + dL, I_{r+1} = I_ev + N_r mod 2
            elif (20 + r1[1]) == (40 + r2[1]) and r1[2] == r2[2]:
                tab[k] = ('C', 20 + r1[1], r1[2]) # constant k_{r+1} = k_fixed, I_{r+1} = I_fixed!
            else:
                tab[k] = ('K_NDEP', r1, r2)
        else:
            tab[k] = ('OTHER', r1[0] + r2[0])

    # Find tail period P for k >= 10
    per = None
    for P in range(1, 10):
        for k0 in range(6, 29 - 2*P):
            if all(tab[k] == tab[k + P] for k in range(k0, 29 - P)):
                per = (P, k0)
                break
        if per: break

    # Now trace from each unique k1 in items:
    by_k1 = defaultdict(list)
    for pname, k1, tm in items:
        by_k1[k1].append((pname, tm))

    for k1, subitems in sorted(by_k1.items()):
        # Initial Round 1 parameters:
        # For k1 == 1: A_1 = 18 (exact!), N_1 = 54 (even!), I_1 = 0
        # For k1 == 2: A_1 = 26,151,766,068 (exact!), N_1 = 78,455,298,203 (odd!), I_1 = 1
        # For k1 == 4: A_1 is tower of height 4 with I_1 = 0 -> use R_tower(0, m)
        traj = []
        curr_k = k1
        curr_I = 0 if k1 in (1, 4) else 1
        curr_exact_A = 18 if k1 == 1 else (26151766068 if k1 == 2 else None)
        outcome = None
        for r in range(1, 50):
            if curr_k <= 28:
                cell = tab[curr_k]
            elif per is not None:
                P, k0 = per
                k_rep = k0 + ((curr_k - k0) % P)
                cell = tab[k_rep]
            else:
                outcome = ('NOPERIOD', r)
                break

            traj.append((r, curr_k, curr_I, cell[0]))
            if cell[0] == 'H':
                outcome = ('HALT', r)
                break
            elif cell[0] == 'C':
                # List-collapsing K rebuild! Wait: let's check if it depends on N_r parity!
                _, k_next, I_ev = cell
                # Check N=21 as well to see if k_next or I_next depends on N_r mod 2
                r_odd = sim_exhaustion(T, curr_k if curr_k <= 28 else k_rep, 21)
                if curr_exact_A is not None:
                    N_r = 3 * curr_exact_A + 1 - curr_k
                else:
                    N_r_mod2 = (3 * curr_I + 1 - curr_k) % 2
                    N_r = 21 if N_r_mod2 == 1 else 20
                if N_r % 2 == 1 and r_odd[0] == 'K':
                    curr_k = 21 + r_odd[1]
                    curr_I = r_odd[2]
                elif N_r % 2 == 1 and r_odd[0] == 'H':
                    traj[-1] = (r, curr_k, curr_I, 'H_oddN')
                    outcome = ('HALT', r)
                    break
                else:
                    curr_k = k_next
                    curr_I = I_ev
                curr_exact_A = 18 if curr_k == 1 else (26151766068 if curr_k == 2 else None)
            elif cell[0] == 'K':
                _, dL, I_ev = cell
                # Also check N=21 in case odd N behaves differently!
                k_lookup = curr_k if curr_k <= 28 else (per[1] + (curr_k - per[1]) % per[0])
                r_odd = sim_exhaustion(T, k_lookup, 21)
                if curr_exact_A is not None:
                    N_r = 3 * curr_exact_A + 1 - curr_k
                    if N_r % 2 == 1 and r_odd[0] != 'K':
                        if r_odd[0] == 'H':
                            traj[-1] = (r, curr_k, curr_I, 'H_oddN')
                            outcome = ('HALT', r)
                            break
                        else:
                            outcome = ('ODD_N_' + r_odd[0], r)
                            break
                    dL_use = r_odd[1] if N_r % 2 == 1 else dL
                    curr_k = N_r + dL_use
                    curr_I = (r_odd[2] if N_r % 2 == 1 else I_ev)
                    curr_exact_A = 18 if curr_k == 1 else (26151766068 if curr_k == 2 else None)
                else:
                    if per is None:
                        outcome = ('NOPERIOD', r)
                        break
                    P, k0 = per
                    Q = P * 2 // math.gcd(P, 2)
                    A_mod = R_tower(curr_I, Q)
                    N_mod = (3 * A_mod + 1 - curr_k) % Q
                    if N_mod % 2 == 1 and r_odd[0] != 'K':
                        if r_odd[0] == 'H':
                            traj[-1] = (r, curr_k, curr_I, 'H_oddN')
                            outcome = ('HALT', r)
                            break
                        else:
                            outcome = ('ODD_N_' + r_odd[0], r)
                            break
                    dL_use = r_odd[1] if N_mod % 2 == 1 else dL
                    # Map curr_k into >= k0 with same residue mod Q
                    k_next_mod = (N_mod + dL_use) % Q
                    curr_k = k0 + ((k_next_mod - k0) % Q)
                    curr_I = r_odd[2] if N_mod % 2 == 1 else (I_ev + N_mod) % 2
                    curr_exact_A = None
            else:
                outcome = (cell[0], r)
                break
        if outcome is None:
            outcome = ('LOOP', 50)
        key = f"{outcome[0]}_R{outcome[1]}"
        stats[key] += len(subitems)
        if outcome[0] == 'HALT' and outcome[1] >= 2:
            halters.append((outcome[1], len(subitems), cat, cdesc, k1, subitems[0][0], subitems[0][1], per, traj))

print("\n=== SUMMARY OF OUTCOMES ACROSS ALL 743 MIXED ROWS ===")
for k, v in sorted(stats.items()):
    print(f"  {k:20s}: {v}")

halters.sort(key=lambda x: (-x[0], -x[1]))
print(f"\n=== GENUINE MULTI-ROUND HALTERS (R >= 2): {len(halters)} groups ({sum(x[1] for x in halters)} machines) ===")
for r, cnt, cat, cdesc, k1, pname, tm, per, traj in halters:
    t_str = " -> ".join(f"R{tr[0]}(k={tr[1]},I={tr[2]}):{tr[3]}" for tr in traj)
    print(f"  [E_{r} HALTER | cnt={cnt:2d} | {cat} {cdesc:10s} | k1={k1} | {pname:15s}] {tm}")
    print(f"      per={per} | {t_str}")
