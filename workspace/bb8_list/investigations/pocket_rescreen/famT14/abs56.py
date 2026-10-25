"""abs56.py: omega-abstraction of eng56 (values int or BIG) from the blank-tape state; reports RB (rebuild) rounds."""
BIG = 'B'
def nb(v): return BIG if v == BIG or v > 10**6 else v
def norm(ds):
    i = 0
    while i < len(ds) and ds[i] == (0, 1): i += 1
    return ds[i:]
def step(ds, b):
    ds = norm(list(ds))
    jm = max([i for i, (v, m) in enumerate(ds) if m == 1], default=-1)
    if any(v != 0 for v, m in ds[jm + 1:]) and len(ds) - jm - 1 >= 2:
        return ds[:jm + 1] + [(0, 0)] * (len(ds) - jm - 1), BIG, 'ZONE*'
    if ds[-1][0] != 0:
        v, m = ds[-1]
        if v == BIG: ds[-1] = (0, m); return ds, BIG, 'R2*'
        ds[-1] = (v - 1, m); return ds, BIG if b == BIG else nb(2 * b + 2), 'R2'
    if ds[-1] == (0, 1):
        ds[-1] = (BIG if b == BIG else b + 1, 0); return ds, 2, 'L0'
    k = 0
    while k < len(ds) and ds[-1 - k] == (0, 0): k += 1
    j = len(ds) - 1 - k
    Zm = [(1, 0)] * (k - 1) + [(2, 1)]
    if j >= 0 and ds[j][0] != 0:
        if ds[j][0] == BIG: return ds[:j] + [(0, ds[j][1])] + ds[j + 1:], BIG, 'R3*'
        return ds[:j] + [(ds[j][0] - 1, ds[j][1])] + [(BIG if b == BIG else b - k, 0)] + [(1, 0)] * (k - 1), 4, 'R3'
    t = BIG if b == BIG else b - k + 1
    if j >= 0: return ds[:j] + [(t, 1)] + Zm, 2, 'RM'
    return [(t, 1)] + Zm, 2, 'RB'
ds, b = [(2, 0)], 2
rounds = 0; it = 0; kinds = {}
while rounds < 6 and it < 10**6:
    ds, b, k = step(ds, b); it += 1; kinds[k] = kinds.get(k, 0) + 1
    if k == 'RB':
        rounds += 1; print('RB #%d at macro %d: len %d top %s' % (rounds, it, len(ds), ds[:3]))
print(kinds)
