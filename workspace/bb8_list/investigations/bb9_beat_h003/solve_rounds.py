"""Exact residue-automaton multi-round solver for 9-state champ_231/232 extensions.

Input: tables_*.txt produced by strict_tables.exe (k = 1..KMAX, two even list lengths N1, N2).

Round model (MULTI_ROUND_PROOF.txt / bb9_champ231_accel Theorems 1-4):
  Round r exhaustion tape = K(A_r; digits) with k_r digits  ->  gadget sees prefix (10)^(2k_r-1)
  and N_r = 3*A_r + 1 - k_r blocks of 1100.  The gadget either halts (H) or rebuilds a clean K
  with k_{r+1} = N_r + dL(k_r) digits and digit-sum parity I_{r+1} = I_ev(k_r) + N_r (mod 2)
  (I_ev = parity measured at even N; every extra untouched 1100 block is one more digit 1).
Accumulator residues (Leftmost-borrow law, the champ_231 analogue of perturb8's Leftmost
Boundary Absorption): every round of length >= 2 ends with B_1 followed by an E_0 drain from a=1:
  2*A_r + 3 = 5 * 3^(3*x + 2),   x = A_penult,  x == 1 - I_r (mod 2),
and x itself has the same form, so A_r mod m is a function of I_r alone (computed by a
Carmichael-tower recursion, R(I, m) below).  Hence (k_r mod Q, I_r) is a finite automaton.
"""
import sys, math
from functools import lru_cache

sys.setrecursionlimit(10000)

def factor(n):
    f = {}
    p = 2
    while p * p <= n:
        while n % p == 0:
            f[p] = f.get(p, 0) + 1
            n //= p
        p += 1
    if n > 1:
        f[n] = f.get(n, 0) + 1
    return f

def carmichael(n):
    if n == 1:
        return 1
    l = 1
    for p, e in factor(n).items():
        if p == 2:
            t = 1 if e == 1 else (2 if e == 2 else 2 ** (e - 2))
        else:
            t = (p - 1) * p ** (e - 1)
        l = l * t // math.gcd(l, t)
    return l

@lru_cache(maxsize=None)
def R(I, m):
    """A mod m for a (huge) champ_231 round accumulator A with A == I (mod 2)."""
    if m == 1:
        return 0
    if m == 2:
        return I  # A == I (mod 2) by definition of I (digit-sum parity invariant)
    m2 = 2 * m
    b = 0
    c = m2
    while c % 3 == 0:
        c //= 3
        b += 1
    p3 = 3 ** b
    # 3^(3x+2) mod c, x == A_penult with parity 1 - I
    if c == 1:
        v_c = 0
    else:
        lam = carmichael(c)
        xr = R(1 - I, lam)
        e = (3 * xr + 2) % lam
        e += lam * 50  # exponent is huge; keep it large and congruent
        v_c = (5 * pow(3, e, c) - 3) % c
    v_p3 = (-3) % p3  # 5*3^(huge) == 0 mod 3^b
    # CRT
    if p3 == 1:
        val = v_c
    elif c == 1:
        val = v_p3
    else:
        t = ((v_p3 - v_c) * pow(c, -1, p3)) % p3
        val = v_c + c * t
    assert (val - 0) % 1 == 0
    # val == 2A+3-3+3? we computed 5*3^e - 3 == 2A mod 2m
    assert val % 2 == 0, (I, m, val)
    return (val // 2) % m

# sanity: parity
assert R(1, 2) == 1 and R(0, 2) == 0, (R(1, 2), R(0, 2))

def load(path):
    rows = []
    raw = open(path, 'rb').read()
    txt = raw.decode('utf-16') if raw[:2] in (b'\xff\xfe', b'\xfe\xff') else raw.decode('utf-8', 'replace')
    for line in txt.splitlines():
        parts = line.rstrip('\n').split('\t')
        if len(parts) < 4:
            continue
        cat, fam, tm = parts[0], parts[1], parts[2]
        tab = {}
        for cell in parts[3:]:
            k, kinds, d1, d2, i1, i2 = cell.split(':')[:6]
            kinds = kinds.upper()
            tab[int(k)] = (kinds, int(d1), int(d2), int(i1), int(i2))
        rows.append((cat, fam, tm, tab))
    return rows

def classify_cell(c):
    kinds, d1, d2, i1, i2 = c
    if kinds == 'HH':
        return ('H',)
    if kinds == 'KK':
        if d1 == d2 and i1 == i2:
            return ('K', d1, i1)          # positional: k_len grows with N (true f_omega round)
        if d1 - d2 == 20:                 # k_len identical for N and N+20 -> list-collapsing
            return ('C', d1 + 0, i1, i2)  # (store dL at N1; k_len = dL1 + N1)
        return ('X',)
    return ('X' + kinds,)

def find_period(cls, kmin_tail, kmax, pmax=40):
    """smallest P and k0 such that cls[k] == cls[k+P] for all k0 <= k <= kmax - P, with
    at least 2 full periods verified."""
    best = None
    for P in range(1, pmax + 1):
        # find smallest k0 such that periodic from k0
        k0 = None
        for start in range(kmin_tail, kmax - 2 * P + 1):
            if all(cls[k] == cls[k + P] for k in range(start, kmax - P + 1)):
                k0 = start
                break
        if k0 is not None:
            return P, k0
    return None

def solve(tab, kmax, k1=20, I1=1, max_rounds=200):
    cls = {k: classify_cell(tab[k]) for k in range(1, kmax + 1)}
    traj = []
    c = cls[k1]
    if c[0] == 'H':
        return ('HALT', 1, traj, None)
    if c[0] != 'K':
        return ('ROUND1_' + c[0], 1, traj, None)
    per = find_period(cls, 12, kmax)
    if per is None:
        return ('NOPERIOD', 1, traj, None)
    P, k0 = per
    Q = P * 2 // math.gcd(P, 2)
    # all classes in periodic regime must be H or K for the automaton
    reg = {}
    for k in range(k0, k0 + Q):
        reg[k % Q] = cls[k]
    # Round 1 (k1 = 20 exact)
    _, dL, Iev = c
    A = R(I1, Q)
    N = (3 * A + 1 - k1)
    k = (N + dL) % Q
    I = (Iev + N) % 2
    traj.append((1, k1, I1, 'K'))
    seen = {}
    for r in range(2, max_rounds):
        st = (k, I)
        cc = reg[k]
        traj.append((r, k, I, cc[0]))
        if cc[0] == 'H':
            return ('HALT', r, traj, (P, k0))
        if cc[0] != 'K':
            return ('REG_' + cc[0], r, traj, (P, k0))
        if st in seen:
            return ('LOOP', r, traj, (P, k0))
        seen[st] = r
        _, dL, Iev = cc
        A = R(I, Q)
        N = 3 * A + 1 - k
        k, I = (N + dL) % Q, (Iev + N) % 2
    return ('MAXR', max_rounds, traj, (P, k0))

if __name__ == '__main__':
    from collections import Counter
    out = open(sys.argv[-1], 'w')
    stats = Counter()
    best = []
    for path in sys.argv[1:-1]:
        rows = load(path)
        for cat, fam, tm, tab in rows:
            kmax = max(tab)
            res, r, traj, per = solve(tab, kmax)
            stats[(res if res != 'HALT' else 'HALT_R%d' % r)] += 1
            hks = [k for k in range(1, kmax + 1) if tab[k][0] == 'HH']
            ncoll = sum(1 for k in range(1, kmax + 1) if classify_cell(tab[k])[0] == 'C')
            line = '%-10s R=%-3d %-18s %s per=%s Hk=%s ncollapse=%d traj=%s' % (
                res, r, fam, tm, per, hks[:12], ncoll,
                ' '.join('R%d(k%%Q=%d,I=%d)%s' % t for t in traj[:12]))
            out.write(line + '\n')
            if res == 'HALT':
                best.append((r, line))
    best.sort(reverse=True)
    out.write('\n=== STATS ===\n')
    for k_, v in sorted(stats.items()):
        out.write('%s: %d\n' % (k_, v))
    out.write('\n=== TOP HALTERS ===\n')
    for r, line in best[:40]:
        out.write(line + '\n')
    print('\n'.join('%s: %d' % kv for kv in sorted(stats.items())))
    for r, line in best[:15]:
        print(line[:330])
