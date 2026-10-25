"""Kd family tools for the BB(10) champion and its relatives (structure to the RIGHT of the head).

Kd ds a b = 0^inf [D on 0] 1^(b+1) 0 1^a 0 1^d1 0 1^d2 0 ... 0 1^dn 0^inf   (ds top digit first = nearest the head)
Trailing zero digits merge into the blank; a parsed list never ends with a 0 digit (stripped).
"""
from tmlit import Sim, ST

CH10 = '1RB1RA_0LC0LF_0RD1LC_1RA1RG_1RZ0RA_1LB1LF_1LH1RE_0LI1LH_0LF0LJ_1LH0LJ'
CH9 = '1RB1RA_0LC0LF_0RD1LC_1RA1RG_1RZ0RA_1LB1LF_1LH1RE_0LI1LH_1LB0LH'


def kword(ds, a, b):
    w = '1' * (b + 1) + '0' + '1' * a
    for d in ds:
        w += '0' + '1' * d
    return w


def kstart(tm, ds, a, b, size=1 << 16):
    w = kword(ds, a, b)
    return Sim.from_word(tm, '0' + w, 0, 'D', size=size)


def parse_at(s):
    """(ds, a, b) if s is in Kd shape (state D, head on 0, blank to the left), else None."""
    if ST[s.state] != 'D':
        return None
    t = s.tape
    p = s.pos
    if t[p] != 0 or t[p + 1] != 1:
        return None
    if any(t[s.lo:p]):
        return None
    hi = s.hi
    while hi > p and t[hi] == 0:
        hi -= 1
    runs = []
    cur = 0
    for i in range(p + 1, hi + 1):
        if t[i]:
            cur += 1
        else:
            runs.append(cur)
            cur = 0
    runs.append(cur)
    if len(runs) < 2:
        runs.append(0)
    b = runs[0] - 1
    a = runs[1]
    ds = runs[2:]
    while ds and ds[-1] == 0:
        ds.pop()
    return (tuple(ds), a, b)


def run_from(s, N=10 ** 7):
    start = s.steps
    while s.steps - start < N:
        if not s.step():
            return ('HALT', s.steps, (ST[s.last[0]], s.last[1]), s)
        if s.state == 3:
            r = parse_at(s)
            if r is not None:
                return ('K', s.steps, r)
    return ('TIMEOUT', s.steps)


def run_next(tm, ds, a, b, N=10 ** 7):
    return run_from(kstart(tm, ds, a, b), N)
