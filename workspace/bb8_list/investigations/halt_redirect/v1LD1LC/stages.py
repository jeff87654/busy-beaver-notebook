"""Stage-map grids for the 1LD1LC machine.  Each stage is a template in -> out (tokens farthest-first, then a, r);
the literal stage server runs the input and the result must equal the template output EXACTLY, else FAIL.
usage: python stages.py STAGE [--quick]     STAGE in S1 S2 S3 S4 S6 S8 S10 S11 ALL"""
import sys, itertools, argparse, time
from lit1 import run, expand, rle, fmt

# real residue classes (numres): r == 19 (mod 2520) for every huge accumulator; m (zeros after J0) == 1075 (mod 2520),
# == 0 (mod 5); u (D9 count) == 520 (mod 2520), m = 2u + 35.
RS = [19, 2539, 5059, 7579, 10099, 12619, 15139]          # all residues mod 11 and 13 differ
RS_SMALL = [19, 2539, 5059]
MS_REAL = [1075, 3595]
MS_SWEEP = list(range(20, 41))                            # every residue mod 5, 7, 8, 9: detects any m-dependence
US = [1, 2, 3, 16, 520]


def check(name, inp, a, r, exp, exp_a, exp_r, stats, verbose=False):
    o = run(inp, a, r)
    ok = o['kind'] == 'K' and o['toks'] == exp and o['a'] == exp_a and o['r'] == exp_r and not o['far']
    stats['n'] += 1
    if not ok:
        stats['bad'] += 1
        print(f'FAIL {name}: in [{rle(inp)} | {a} | {r}]\n   got {fmt(o)}\n   exp K: {rle(exp)} | a={exp_a} r={exp_r}', flush=True)
    elif verbose:
        print(f'ok {name}: {fmt(o)}', flush=True)
    return ok


FULL = False
def grid(quick, **kw):
    """parameter lists per mode: kw values are (quick_list, std_list, full_list)"""
    return {k: (v[0] if quick else v[2] if FULL else v[1]) for k, v in kw.items()}

def S1(st, quick):
    # [9^u 8 3 1^z | 1 | r] -> [9^u 8 0 (2r+5) 1^(z-1) | 1 | 1]   (an R3 step from D3; also S3/S5/S7/S9 with other prefixes)
    for u, z, r in itertools.product([1, 2, 16], MS_REAL + MS_SWEEP, RS_SMALL if quick else RS):
        inp = [9] * u + [8, 3] + [1] * z
        check(f'S1 u={u} z={z} r={r}', inp, 1, r, [9] * u + [8, 0, 2 * r + 5] + [1] * (z - 1), 1, 1, st)


def S2(st, quick):
    # [9^u 8 0 1^z | 1 | r] -> [9^(u-1) 5 3 0 3 (2r+3) 1^(z+2) | 1 | 2]
    for u, z, r in itertools.product(US, MS_REAL + MS_SWEEP, RS_SMALL if quick else RS):
        inp = [9] * u + [8, 0] + [1] * z
        check(f'S2 u={u} z={z} r={r}', inp, 1, r, [9] * (u - 1) + [5, 3, 0, 3, 2 * r + 3] + [1] * (z + 2), 1, 2, st)


def S3(st, quick):
    # [9^(u-1) 5 3 0 3 (2A) 3 1^z | 1 | r] -> [.. (2A) 0 (2r+5) 1^(z-1) | 1 | 1]
    for u, z, A, r in itertools.product([1, 3, 16], MS_REAL + MS_SWEEP[:6], RS_SMALL, RS_SMALL if quick else RS):
        inp = [9] * (u - 1) + [5, 3, 0, 3, 2 * A, 3] + [1] * z
        check(f'S3 u={u} z={z} A={A} r={r}', inp, 1, r, [9] * (u - 1) + [5, 3, 0, 3, 2 * A, 0, 2 * r + 5] + [1] * (z - 1), 1, 1, st)


def S4(st, quick):
    # [9^(u-1) 5 3 0 3 (2A) 0 1^z | 1 | r] -> [9^(u-1) 2 7 0 0 3 3 (0 3)^((A-5)/2) 0 (2r+3) 1^(z+2) | 1 | 2]
    for u, z, A, r in itertools.product([1, 2, 3, 16, 520], MS_REAL + MS_SWEEP, RS_SMALL, RS_SMALL if quick else RS):
        if quick and u == 520 and z > 100:
            continue
        inp = [9] * (u - 1) + [5, 3, 0, 3, 2 * A, 0] + [1] * z
        exp = [9] * (u - 1) + [2, 7, 0, 0, 3, 3] + [0, 3] * ((A - 5) // 2) + [0, 2 * r + 3] + [1] * (z + 2)
        check(f'S4 u={u} z={z} A={A} r={r}', inp, 1, r, exp, 1, 2, st)


def S6(st, quick):
    # [9^(u-1) 2 7 0 0 3 3 (0 3)^k 0 (2A') 0 1^z | 1 | r]
    #   -> [9^(u-1) 2 7 0 0 3 3 (0 3)^(k-2) 0 0 5 (1 0)^(A'-11) 0 1 1 7 1 1 0 3 3 (0 3)^((r+1)/2) 0 7 1^(z+3) | 1 | 2]
    for u, z, k, A, r in itertools.product([1, 3, 16], MS_REAL + MS_SWEEP, [2, 3, 7, 50, 1267], RS_SMALL, RS_SMALL if quick else RS):
        if quick and k == 1267 and (z > 100 or r > 2539):
            continue
        inp = [9] * (u - 1) + [2, 7, 0, 0, 3, 3] + [0, 3] * k + [0, 2 * A, 0] + [1] * z
        exp = ([9] * (u - 1) + [2, 7, 0, 0, 3, 3] + [0, 3] * (k - 2) + [0, 0, 5] + [1, 0] * (A - 11) + [0, 1, 1, 7, 1, 1, 0, 3, 3]
               + [0, 3] * ((r + 1) // 2) + [0, 7] + [1] * (z + 3))
        check(f'S6 u={u} z={z} k={k} A={A} r={r}', inp, 1, r, exp, 1, 2, st)


def PRE6(u, k, A):
    return [9] * (u - 1) + [2, 7, 0, 0, 3, 3] + [0, 3] * k + [0, 0, 5] + [1, 0] * (A - 11) + [0, 1, 1, 7, 1, 1, 0, 3, 3]


def S8(st, quick):
    # [Q (0 3)^j 0 4 0 1^z | 1 | r] -> [Q (0 3)^(j-3) 0 2 1 1 (2r+5) 1^4 0 0 9 1^(z-3) | 1 | 1]
    for u, z, j, A, r in itertools.product([1, 3], MS_REAL + MS_SWEEP, [3, 4, 10, 1270], [19, 2539], RS_SMALL if quick else RS):
        if quick and j == 1270 and (z > 100 or r > 2539):
            continue
        Q = PRE6(u, 5, A)
        inp = Q + [0, 3] * j + [0, 4, 0] + [1] * z
        exp = Q + [0, 3] * (j - 3) + [0, 2, 1, 1, 2 * r + 5, 1, 1, 1, 1, 0, 0, 9] + [1] * (z - 3)
        check(f'S8 u={u} z={z} j={j} A={A} r={r}', inp, 1, r, exp, 1, 1, st)


def S10(st, quick):
    # [Q' (2P+5) 1^4 0 0 0 1^z | 1 | r] -> [Q' (2P+5) 1 0 1 (2r+3) 1^(z+1) | 1 | 1]    P = parked (R8), both size orders
    for u, z, j, P, r in itertools.product([1, 3], MS_REAL + MS_SWEEP, [1, 7], RS_SMALL if quick else RS, RS_SMALL if quick else RS):
        Q = PRE6(u, 5, 19) + [0, 3] * j + [0, 2, 1, 1]
        inp = Q + [2 * P + 5, 1, 1, 1, 1, 0, 0, 0] + [1] * z
        exp = Q + [2 * P + 5, 1, 0, 1, 2 * r + 3] + [1] * (z + 1)
        check(f'S10 u={u} z={z} j={j} P={P} r={r}', inp, 1, r, exp, 1, 1, st)


def S11(st, quick):
    # [Q' (2P+5) 1 0 1 2 1^z | 1 | r] -> HALT I reading 0.  The ones count depends on z mod 5; the real class is
    # z = m+2 == 2 (mod 5).  Fit ones = affine in (u, z, k, A, j, P, r) separately per class z mod 5; verify exactly.
    rows = []
    ZS = [1077, 3597, 22, 27, 32, 37] if quick else [1077, 3597] + list(range(20, 45))
    for u, z, k, A, j, P, r in itertools.product([1, 3, 5], ZS, [5, 6, 20], [19, 2539], [1, 7, 30],
                                                 RS_SMALL if quick else RS, RS_SMALL if quick else RS):
        if quick and (z > 100 and (P > 2539 or r > 2539)):
            continue
        Q = PRE6(u, k, A) + [0, 3] * j + [0, 2, 1, 1]
        inp = Q + [2 * P + 5, 1, 0, 1, 2] + [1] * z
        o = run(inp, 1, r)
        st['n'] += 1
        if o['kind'] != 'H' or o['state'] != 'I' or o['read'] != 0:
            st['bad'] += 1
            print(f'FAIL S11 u={u} z={z} k={k} A={A} j={j} P={P} r={r}: {fmt(o)}', flush=True)
            continue
        rows.append(((u, z, k, A, j, P, r), o['ones'], o['step']))
    from fractions import Fraction
    import numpy as np, json
    coefs = {}
    for cls in sorted(set(x[1] % 5 for x, _, _ in rows)):
        sub = [(x, o, s) for x, o, s in rows if x[1] % 5 == cls]
        X = np.array([[1] + list(x) for x, _, _ in sub], dtype=float)
        y = np.array([o for _, o, _ in sub], dtype=float)
        co, *_ = np.linalg.lstsq(X, y, rcond=None)
        co = [Fraction(c).limit_denominator(1000) for c in co]
        bad = 0
        for x, o, s in sub:
            pred = co[0] + sum(c * v for c, v in zip(co[1:], x))
            if pred != o:
                bad += 1
                if bad < 6:
                    print(f'ONES MISFIT (z mod 5 = {cls}) {x}: got {o} pred {pred}')
        st['bad'] += bad
        coefs[cls] = [str(c) for c in co]
        print(f'S11 z mod 5 = {cls}: ones = {co[0]} + {co[1]}*u + {co[2]}*z + {co[3]}*k + {co[4]}*A + {co[5]}*j + {co[6]}*P + {co[7]}*r'
              f'   ({len(sub)} halts, {bad} misfits)', flush=True)
    json.dump(coefs, open('ones_coef.json', 'w'))
    stp = sorted(set(s for _, _, s in rows))
    print(f'S11 steps: min {stp[0]} max {stp[-1]}; {len(rows)} halts of {st["n"]} cases')


ALL = dict(S1=S1, S2=S2, S3=S3, S4=S4, S6=S6, S8=S8, S10=S10, S11=S11)
if __name__ == '__main__' and '--full' not in sys.argv:
    ap = argparse.ArgumentParser(); ap.add_argument('stage'); ap.add_argument('--quick', action='store_true')
    a = ap.parse_args()
    names = list(ALL) if a.stage == 'ALL' else a.stage.split(',')
    total = {'n': 0, 'bad': 0}
    for nm in names:
        st = {'n': 0, 'bad': 0}; t0 = time.time()
        ALL[nm](st, a.quick)
        print(f'== {nm}: {st["n"]} cases, {st["bad"]} mismatches, {time.time()-t0:.0f}s', flush=True)
        total['n'] += st['n']; total['bad'] += st['bad']
    print(f'TOTAL {total["n"]} cases, {total["bad"]} mismatches')
    if total['bad']:
        sys.exit(1)


def FULLRUN():
    """--full: every stage with r (and the parked tokens that the stage reads) over all 7 residue representatives,
    z in {1075 (real class), 31}, two u values; both size orders for parked vs current"""
    st = {'n': 0, 'bad': 0}
    Z = [1075, 30]                      # S1/S2 input zeros = m (real m == 1075 mod 2520, == 0 mod 5)
    for u, z, r in itertools.product([1, 3], Z, RS):
        check(f'S1 u={u} z={z} r={r}', [9] * u + [8, 3] + [1] * z, 1, r, [9] * u + [8, 0, 2 * r + 5] + [1] * (z - 1), 1, 1, st)
        check(f'S2 u={u} z={z} r={r}', [9] * u + [8, 0] + [1] * z, 1, r, [9] * (u - 1) + [5, 3, 0, 3, 2 * r + 3] + [1] * (z + 2), 1, 2, st)
    print(f'S1,S2 done: {st}', flush=True)
    Z = [1076, 31]                      # S3/S4: m+1
    for u, z, A, r in itertools.product([1, 3], Z, [19, 5059, 15139], [19, 7579, 15139]):
        check(f'S3 u={u} z={z} A={A} r={r}', [9] * (u - 1) + [5, 3, 0, 3, 2 * A, 3] + [1] * z, 1, r,
              [9] * (u - 1) + [5, 3, 0, 3, 2 * A, 0, 2 * r + 5] + [1] * (z - 1), 1, 1, st)
        check(f'S4 u={u} z={z} A={A} r={r}', [9] * (u - 1) + [5, 3, 0, 3, 2 * A, 0] + [1] * z, 1, r,
              [9] * (u - 1) + [2, 7, 0, 0, 3, 3] + [0, 3] * ((A - 5) // 2) + [0, 2 * r + 3] + [1] * (z + 2), 1, 2, st)
    print(f'S3,S4 done: {st}', flush=True)
    Z = [1077, 32]                      # S6: m+2
    for u, z, k, A, r in itertools.product([1, 3], Z, [2, 7], [19, 5059, 15139], [19, 7579, 15139]):
        inp = [9] * (u - 1) + [2, 7, 0, 0, 3, 3] + [0, 3] * k + [0, 2 * A, 0] + [1] * z
        exp = ([9] * (u - 1) + [2, 7, 0, 0, 3, 3] + [0, 3] * (k - 2) + [0, 0, 5] + [1, 0] * (A - 11) + [0, 1, 1, 7, 1, 1, 0, 3, 3]
               + [0, 3] * ((r + 1) // 2) + [0, 7] + [1] * (z + 3))
        check(f'S6 u={u} z={z} k={k} A={A} r={r}', inp, 1, r, exp, 1, 2, st)
    print(f'S6 done: {st}', flush=True)
    Z = [1079, 34]                      # S8: m+4
    for u, z, j, A, r in itertools.product([1, 3], Z, [3, 10], [19, 15139], RS):
        Q = PRE6(u, 5, A)
        check(f'S8 u={u} z={z} j={j} A={A} r={r}', Q + [0, 3] * j + [0, 4, 0] + [1] * z, 1, r,
              Q + [0, 3] * (j - 3) + [0, 2, 1, 1, 2 * r + 5, 1, 1, 1, 1, 0, 0, 9] + [1] * (z - 3), 1, 1, st)
    print(f'S8 done: {st}', flush=True)
    Z = [1076, 31]                      # S10: m+1
    for u, z, P, r in itertools.product([1, 3], Z, RS, RS):
        Q = PRE6(u, 5, 19) + [0, 3] * 7 + [0, 2, 1, 1]
        check(f'S10 u={u} z={z} P={P} r={r}', Q + [2 * P + 5, 1, 1, 1, 1, 0, 0, 0] + [1] * z, 1, r,
              Q + [2 * P + 5, 1, 0, 1, 2 * r + 3] + [1] * (z + 1), 1, 1, st)
    print(f'S10 done: {st}', flush=True)
    rows = []
    Z = [1077, 32]                      # S11: m+2 (== 2 mod 5, the real class)
    for u, z, k, A, j, P, r in itertools.product([1, 3], Z, [5, 20], [19, 15139], [1, 30], RS, RS):
        Q = PRE6(u, k, A) + [0, 3] * j + [0, 2, 1, 1]
        o = run(Q + [2 * P + 5, 1, 0, 1, 2] + [1] * z, 1, r)
        st['n'] += 1
        if o['kind'] != 'H' or o['state'] != 'I' or o['read'] != 0:
            st['bad'] += 1
            print(f'FAIL S11 u={u} z={z} k={k} A={A} j={j} P={P} r={r}: {fmt(o)}', flush=True)
            continue
        rows.append(((u, z, k, A, j, P, r), o['ones'], o['step']))
    bad = 0
    for x, o, s in rows:
        u, z, k, A, j, P, r = x
        pred = ONES(u, z, k, A, j, P, r)
        if pred != o:
            bad += 1
            if bad < 10:
                print(f'ONES MISFIT {x}: got {o} pred {pred}')
    st['bad'] += bad
    print(f'S11 done: {len(rows)} halts, {bad} ones misfits; steps min {min(s for _,_,s in rows)} max {max(s for _,_,s in rows)}')
    print(f'FULL TOTAL {st["n"]} cases, {st["bad"]} mismatches')
    return st['bad']


def ONES(u, z, k, A, j, P, r):
    """ones at the halt of S11 (fitted by the quick grid per class z mod 5)"""
    c = ONES_COEF[str(z % 5)]
    return c[0] + c[1] * u + c[2] * z + c[3] * k + c[4] * A + c[5] * j + c[6] * P + c[7] * r


ONES_COEF = None
if __name__ == '__main__' and '--full' in sys.argv:
    FULL = True
    import json
    ONES_COEF = {k: [__import__('fractions').Fraction(x) for x in v] for k, v in json.load(open('ones_coef.json')).items()}
    sys.exit(1 if FULLRUN() else 0)
