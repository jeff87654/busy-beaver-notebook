"""Family K(ds; a; b) = 0^inf 1^d1 0 1^d2 0 ... 0 1^dn 0 1^a 0 1^b 0 1 B>0 0^inf   (d1 >= 1 or n = 0).
Literal simulation from K until the next configuration of the same shape (state B reading blank at the right
end, with 0 1 immediately to its left) and parse it."""
import sys
from fromcfg import make
from lit import ST, MAIN
def kword(ds, a, b):
    w = ''
    for d in ds:
        w += '1' * d + '0'
    w += '1' * a + '0' + '1' * b + '01'
    return w.lstrip('0')
def kstart(ds, a, b, tm=MAIN):
    w = kword(ds, a, b)
    return make('0' * 4 + w + '0', 4 + len(w), 'B', tm=tm, size=1 << 16)
def parse(s):
    """if s is in K-shape return (ds, a, b) else None"""
    t = s.tape; p = s.pos
    if s.state != 1 or t[p] != 0 or p < s.hi: return None
    if not (t[p - 1] == 1 and t[p - 2] == 0): return None
    lo = s.lo
    while lo < p and t[lo] == 0: lo += 1
    runs = []; i = p - 3
    # parse runs leftwards separated by single zeros
    cur = 0
    while i >= lo:
        if t[i] == 1: cur += 1
        else: runs.append(cur); cur = 0
        i -= 1
    runs.append(cur)
    runs.reverse()
    if len(runs) < 2: return None
    ds = runs[:-2]; a, b = runs[-2], runs[-1]
    if ds and ds[0] == 0: return None
    return (tuple(ds), a, b)
def run_next(ds, a, b, N=10**8, tm=MAIN):
    s = kstart(ds, a, b, tm)
    while s.steps < N:
        if not s.step():
            return ('HALT', s.steps)
        r = parse(s)
        if r is not None:
            return ('K', s.steps, r)
    return ('TIMEOUT', s.steps)
def predict(ds, a, b):
    ds = list(ds)
    if a >= 1: return (tuple(ds), a - 1, 4 * b + 4)
    # a == 0
    k = 0
    while k < len(ds) and ds[len(ds) - 1 - k] == 0: k += 1
    if k == len(ds):  # all zero -> blank (ds nonempty only if leading zeros... normalized: ds empty)
        return (tuple([2] + [1] * (4 * b)), 1, 1)
    if k == 0:
        ds[-1] -= 1
        out = (ds, 4 * b + 3, 1)
    else:
        i = len(ds) - 1 - k
        ds[i] -= 1
        ds = ds[:i + 1] + [4 * b + 3 - k] + [1] * (k - 1)
        out = (ds, 1, 1)
    ds, a2, b2 = out
    while ds and ds[0] == 0: ds = ds[1:]
    return (tuple(ds), a2, b2)
if __name__ == '__main__':
    print(run_next((2,), 1, 1))
