"""Generalised residue solver: per residue class s (mod P) the gadget outcome kind is constant and
dL, I_ev are AFFINE in t = (k - s0)/P:  dL(k) = dL(s0) + c_s * t,  I(k) = I(s0) + e_s * t (mod 2).
(Periodic tables are the special case c_s = e_s = 0.)  k_r is tracked modulo a shrinking modulus
L = P^D * m (one factor P of precision is consumed per round), which is exact for D rounds."""
import sys, math
from solve_rounds import load, classify_cell, R

M0 = 2**6 * 3**4 * 5**2 * 7 * 11 * 13

def fit(cls, kmax, kmin=12, pmax=24):
    for P in range(1, pmax + 1):
        for k0 in range(kmin, kmax - 3 * P + 1):
            ok = True
            model = {}
            for s0 in range(k0, k0 + P):
                ks = list(range(s0, kmax + 1, P))
                if len(ks) < 3:
                    ok = False; break
                kinds = {cls[k][0] for k in ks}
                if len(kinds) != 1:
                    ok = False; break
                kd = kinds.pop()
                if kd == 'H':
                    model[s0 % P] = ('H', s0); continue
                if kd != 'K':
                    ok = False; break
                dls = [cls[k][1] for k in ks]
                Is = [cls[k][2] for k in ks]
                c = dls[1] - dls[0]
                if any(dls[i + 1] - dls[i] != c for i in range(len(dls) - 1)):
                    ok = False; break
                e = (Is[1] - Is[0]) % 2
                if any((Is[i + 1] - Is[i]) % 2 != e for i in range(len(Is) - 1)):
                    ok = False; break
                model[s0 % P] = ('K', s0, dls[0], c, Is[0], e)
            if ok:
                return P, k0, model
    return None

def solve2(tab, kmax, k1=20, I1=1, D=14):
    cls = {k: classify_cell(tab[k]) for k in range(1, kmax + 1)}
    c1 = cls[k1]
    if c1[0] == 'H':
        return ('HALT', 1, [], None)
    if c1[0] != 'K':
        return ('R1_' + c1[0], 1, [], None)
    f = fit(cls, kmax)
    if f is None:
        return ('NOFIT', 1, [], None)
    P, k0, model = f
    L = P ** D * M0
    _, dL, Iev = c1
    A = R(I1, L)
    N = 3 * A + 1 - k1
    k = (N + dL) % L
    I = (Iev + N) % 2
    traj = [(1, k1 % P, I1, 'K')]
    for r in range(2, D):
        s = k % P
        m = model[s]
        traj.append((r, s, I, m[0]))
        if m[0] == 'H':
            return ('HALT', r, traj, (P, k0))
        _, s0, dl0, c, i0, e = m
        Ln = L // P
        t = ((k - s0) // P) % Ln      # exact since k == s0 (mod P) and L divisible by P
        dLk = (dl0 + c * t) % Ln
        Ik = (i0 + e * t) % 2
        A = R(I, Ln)
        N = (3 * A + 1 - k) % Ln
        k = (N + dLk) % Ln
        I = (Ik + N) % 2
        L = Ln
    return ('ALIVE>=%d' % D, D, traj, (P, k0))

if __name__ == '__main__':
    from collections import Counter
    out = open(sys.argv[-1], 'w')
    st = Counter(); best = []
    for path in sys.argv[1:-1]:
        for cat, fam, tm, tab in load(path):
            kmax = max(tab)
            res, r, traj, per = solve2(tab, kmax)
            st[res if res != 'HALT' else 'HALT_R%d' % r] += 1
            line = '%-10s R=%-3d %-22s %s fit=%s traj=%s' % (res, r, fam, tm, per,
                   ' '.join('R%d(s=%d,I=%d)%s' % t for t in traj))
            out.write(line + '\n')
            if res == 'HALT':
                best.append((r, line))
    best.sort(key=lambda x: -x[0])
    out.write('\n=== STATS ===\n' + '\n'.join('%s: %d' % kv for kv in sorted(st.items())) + '\n')
    out.write('\n=== TOP ===\n' + '\n'.join(l for _, l in best[:40]) + '\n')
    print('\n'.join('%s: %d' % kv for kv in sorted(st.items())))
    for _, l in best[:10]:
        print(l[:300])
