"""abs34.py: omega-abstraction of eng34 (values int or BIG); runs a round from [P,M2,1^N], b until REBUILD/M0-ALONE.
Macro for a BIG digit x with only unmarked zeros below: all its decrements at once -> x=(0,m), b=BIG (sound: lower zone has no marks)."""
import sys
BIG = 'B'
CAP = 10**6
def big(v): return v == BIG or v > CAP
def nb(v): return BIG if big(v) else v
def rmerge(y):
    v, m = y
    if v == BIG: return (BIG, 1 - m)
    r = 2 * v + m + 1; return (r // 2, r % 2)
def step(ds, b):
    ds = list(ds)
    # zone macro: unmarked digits below the lowest marked digit exhaust to zeros (b BIG) if any is nonzero
    jm = max([i for i, (v, m) in enumerate(ds) if m == 1], default=-1)
    if any(v != 0 for v, m in ds[jm + 1:]) and len(ds) - jm - 1 >= 2:
        return ds[:jm + 1] + [(0, 0)] * (len(ds) - jm - 1), BIG, 'ZONE*'
    if ds and ds[-1][0] != 0:
        v, m = ds[-1]
        if v == BIG: ds[-1] = (0, m); return ds, BIG, 'R2*'
        ds[-1] = (v - 1, m); return ds, nb(2 * b + 4) if b != BIG else BIG, 'R2'
    if ds and ds[-1] == (0, 1):
        nb2 = BIG if b == BIG else nb(2 * b + 3)
        if len(ds) >= 2: return ds[:-2] + [rmerge(ds[-2])], nb2, 'M0low-merge'
        return ds, nb2, 'M0-ALONE'
    k = 0
    while k < len(ds) and ds[-1 - k] == (0, 0): k += 1
    j = len(ds) - 1 - k
    if j < 0: return ds, b, 'REBUILD'
    x = ds[j]
    if x[0] != 0:
        if x[0] == BIG: return ds[:j] + [(0, x[1])] + ds[j + 1:], BIG, 'R3*'
        top = BIG if b == BIG else b - k + 2
        assert top == BIG or top >= 0
        return ds[:j] + [(x[0] - 1, x[1])] + [(top, 0)] + [(1, 0)] * (k - 1), 2, 'R3'
    top = BIG if b == BIG else b - k + 1
    assert top == BIG or top >= 0
    Z = [(top, 1)] + [(1, 0)] * (k - 1)
    if j >= 1: return ds[:j - 1] + [rmerge(ds[j - 1])] + Z, 2, 'merge'
    return ds[:j + 1] + Z, 2, 'top-M0'
def run(ds, b, maxit=10**7):
    kinds = {}; it = 0
    while it < maxit:
        ds, b, k = step(ds, b); kinds[k] = kinds.get(k, 0) + 1; it += 1
        if k in ('REBUILD', 'M0-ALONE'): return k, ds, b, kinds, it
    return 'MAXIT', ds, b, kinds, it
if __name__ == '__main__':
    for N in [int(x) for x in sys.argv[1:]]:
        r = run([(0, 1), (2, 1)] + [(1, 0)] * N, 2)
        print('N=%d ->' % N, r[0], 'final ds', r[1][:3], 'len', len(r[1]), 'b', r[2], 'merges', r[3].get('merge', 0), 'steps', r[4])
