"""check2.py: lead's extra checks.
(1) payment: every borrow from the parked digit (X = D(2R-7) in J1, D(2R'+5) in J2) is a literal R3 whose result does not
    depend on the size order of the digit vs the current accumulator r (r from 1 = the real start value, to >> digit).
(2) crossed zeros: for each borrow of a period, the literal head excursion (minpos) is mapped to the token it reached;
    the tokens strictly between it and the a-token are counted and must all be zero digits (D1)."""
import sys, itertools
import c1lib
def tokpos(toks):
    pos, out = 0, []
    for t in toks: out.append((pos, pos + 2 * t)); pos += 2 * t + 1
    return out
def crossed(toks, minpos):
    """index of the token containing minpos; returns (#tokens between it and the a-token, all of them D1?)"""
    tp = tokpos(toks)
    idx = next(i for i, (s, e) in enumerate(tp) if s <= minpos <= e)
    between = toks[idx + 1:-2]
    return idx, len(between), all(x == 1 for x in between)
bad = 0; n_ok = 0
def chk(label, toks, tgt, expect_cross):
    global bad, n_ok
    f = c1lib.reach(toks, tgt, maxs=4 * 10**9)
    if f[0] != 'REACHED':
        bad += 1; print('BAD', label, f[:4], flush=True); return
    idx, k, allz = crossed(toks, int(f[2]))
    ok = k == expect_cross and allz
    if not ok: bad += 1; print('BADCROSS', label, 'reached token', idx, toks[idx], 'crossed', k, 'zeros-only', allz, 'expected', expect_cross, flush=True)
    else: n_ok += 1
    return k
cases = [(20, 117), (8, 169), (2, 195), (5, 1003), (1408, 3220)]          # (p, n) from the b=6 / b=366 chains + one extra
for p, n in cases:
    for X, r in itertools.product([31, 5071, 35317], [1, 19, 2539, 17659]):   # X = 2R-7 for R = 19, 2539, 17662
        # (1)+(2) J1: borrow from the parked X at depth n (r = 1 is the real value; others test size order)
        chk(f'J1-X p{p} n{n} X{X} r{r}', [6]*p + [4, X] + [1]*n + [1, r], [6]*p + [4, X-3, 2*r+5] + [1]*(n-1) + [1, 1], n)
    for r in [19, 2539, 17659]:
        chk(f'J1-Xlast n{n} r{r}', [6]*p + [4, 4] + [1]*n + [1, r], [6]*p + [4, 1, 2*r+5] + [1]*(n-1) + [1, 1], n)
        chk(f'J1-4 n{n} r{r}', [6]*p + [4, 1] + [1]*n + [1, r], [6]*p + [1, 2*r+5] + [1]*n + [1, 1], n + 1)
        chk(f'J1-6 n{n} r{r}', [6]*p + [1, 1] + [1]*n + [1, r], [6]*(p-1) + [3, 2*r+5] + [1]*(n+1) + [1, 1], n + 2)
        chk(f'PARK n{n} r{r}', [6]*(p-1) + [3] + [1]*(n+2) + [1, r], [6]*(p-1) + [0, 2*r+5] + [1]*(n+1) + [1, 1], n + 2)
    for D, r in itertools.product([43, 5083, 35329], [1, 19, 2539, 17659]):  # D = 2R'+5 parked by PARK, cleared by J2
        chk(f'J2-D n{n} D{D} r{r}', [6]*(p-1) + [0, D] + [1]*(n+1) + [1, r], [6]*(p-1) + [0, D-3, 2*r+5] + [1]*n + [1, 1], n + 1)
    for r in [19, 2539]:
        chk(f'J2-Dlast n{n} r{r}', [6]*(p-1) + [0, 4] + [1]*(n+1) + [1, r], [6]*(p-1) + [0, 1, 2*r+5] + [1]*n + [1, 1], n + 1)
    print('done', p, n, 'ok', n_ok, 'bad', bad, flush=True)
print('TOTAL ok', n_ok, 'bad', bad)
