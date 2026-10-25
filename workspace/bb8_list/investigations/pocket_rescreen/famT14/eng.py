"""Abstract engine for T1/T2 (mirrored): K-config = (ds, a, b), ds = list of (value, mark) top->bottom.
Tape runs: digit (v,m) -> run 2v+m; then runs 2a, 2b; then 00, head in B on next cell."""
def to_runs(ds, a, b):
    return [2 * v + m for v, m in ds] + [2 * a, 2 * b]
def from_runs(r):
    return [(x // 2, x % 2) for x in r[:-2]], (r[-2] // 2 if r[-2] % 2 == 0 else ("odd", r[-2])), (r[-1] // 2 if r[-1] % 2 == 0 else ("odd", r[-1]))
def borrow(ds, b):
    """a == 0 and d_1 == 0 (or ds all zero). Returns (ds', 2, 0) or None if outside validity."""
    j = max([i for i, (v, m) in enumerate(ds) if v > 0], default=-1)
    Z = ds[j + 1:]
    new = []
    for t, (v, m) in enumerate(Z):
        if t == 0: new.append([None, m]); continue
        new.append([0 if Z[t - 1][1] == 1 else 1, m])
    if j >= 0:
        rem = b - 1 - sum(x[0] for x in new[1:])
        if rem < 0: return None
        new[0][0] = rem
        out = ds[:j] + [(ds[j][0] - 1, ds[j][1])] + [tuple(x) for x in new]
    else:
        new[0][0] = 1
        R = b - sum(x[0] for x in new)
        if R < 1: return None
        out = [(1, 1)] + [(1, 0)] * (R - 1) + [tuple(x) for x in new]
    return out, 2, 0
def step(ds, a, b):
    """one rule application -> next K-config at which a == 0 (macro) """
    if a > 0: return ds, 0, b + 2 * a
    if ds and ds[-1][0] > 0:
        ds = ds[:-1] + [(ds[-1][0] - 1, ds[-1][1])]
        return ds, b + 1, 0
    return borrow(ds, b)
