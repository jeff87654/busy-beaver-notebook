"""stages.py: grid checks of every literal stage of c1's chain (own simulator, exact target K-moments).
Notation: tokens farthest-first, last two = a-token, accumulator r.  m = D6 count, z = zero count, R = accumulator.
Reports per stage: checks, failures, and the minimum number of untouched leading D6 tokens (head confinement: if >= 1 the
map holds for every larger m, since the head never reaches the farther D6s)."""
import sys, itertools, collections
import c1lib
R_DENSE = [19, 22, 25, 43, 97, 100]
R_REAL = [2539, 7579, 17659]          # = r* mod 5040, 10080, 80640 (tower.py)
def S(name):
    # (input(m, z, R), target(m, z, R), m_min)
    return STAGES[name]
STAGES = {
 'T2':  (lambda m, z, R: [6] * m + [2, 0, 0] + [1] * z + [1, R],  lambda m, z, R: [6] * (m - 1) + [3, 2, 1, 0, 2 * R + 4] + [1] * (z - 1) + [1, 1], 1),
 'T4':  (lambda m, z, R: [6] * m + [3, 2, 1, 0, 0] + [1] * z + [1, R], lambda m, z, R: [6] * m + [0, 3, 1, 2 * R + 2] + [1] * (z + 1) + [1, 1], 0),
 'T6':  (lambda m, z, R: [6] * m + [0, 0] + [1] * z + [1, R],       lambda m, z, R: [6] * (m - 1) + [2, 2, 0, 2 * R + 4] + [1] * (z - 1) + [1, 1], 1),
 'T8':  (lambda m, z, R: [6] * m + [2, 2, 0, 0] + [1] * z + [1, R], lambda m, z, R: [6] * (m - 1) + [3, 3, 1, 1, 2 * R + 3] + [1] * z + [1, 1], 1),
 'T9':  (lambda m, z, R: [6] * m + [3, 3, 1, 1, 2] + [1] * z + [1, R], lambda m, z, R: [6] * m + [3, 0, 2 * R + 5, 7] + [1] * (z + 1) + [1, 1], 0),
 'T10': (lambda m, z, R: [6] * m + [3, 0] + [1] * z + [1, R],       lambda m, z, R: [6] * (m - 1) + [4, 2 * R - 1] + [1] * (z + 5) + [1, 1], 1),
 'PARK': (lambda m, z, R: [6] * m + [3] + [1] * z + [1, R],         lambda m, z, R: [6] * m + [0, 2 * R + 5] + [1] * (z - 1) + [1, 1], 0),
 'GROW': (lambda m, z, R: [6] * m + [0] + [1] * z + [1, R],         lambda m, z, R: [6] * (m - 2) + [4, 2 * R - 7] + [1] * (z + 11) + [1, 1], 2),
}
def untouched(toks, minpos):
    pos = 0; k = 0
    for t in toks:
        end = pos + 2 * t                      # last cell of the token
        if t == 6 and end < minpos - 1: k += 1; pos = end + 1
        else: break
    return k
def run(name, ms, zs, Rs, maxs=4 * 10**9):
    fin, ftg, mmin = STAGES[name]
    n = 0; bad = []; unt = None; slots = collections.Counter()
    for m, z, R in itertools.product(ms, zs, Rs):
        if m < mmin: continue
        toks = fin(m, z, R); tgt = ftg(m, z, R)
        f = c1lib.reach(toks, tgt, maxs=maxs); n += 1
        if f[0] != 'REACHED':
            bad.append((m, z, R, ' '.join(f[:6]))); print('  BAD', name, m, z, R, f[:6], flush=True); continue
        k = untouched(toks, int(f[2])); slots[f[3]] += 1
        if m >= 3: unt = k if unt is None else min(unt, k)
    print(f'{name}: {n} checks, {len(bad)} bad, min untouched leading D6 (m>=3) = {unt}, slots {dict(slots)}', flush=True)
    return bad
if __name__ == '__main__':
    which = sys.argv[1:] or list(STAGES)
    for name in which:
        mmin = STAGES[name][2]
        ms = [mmin, mmin + 1, mmin + 2, mmin + 3, 12, 40]
        run(name, ms, list(range(2, 41)) + [77, 160], R_DENSE)
        run(name, [mmin + 1, 30], [50, 113, 301, 1000], R_REAL)
