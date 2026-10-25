"""K-family tools for neighbors of the digit-list counter
    parent = 1RB1RA_0RC0RA_0LD1RC_1RE1LE_1LF0LG_1LB0RD_0LH1LF_1RF---

K(ds; a; b) = 0^inf 1^d1 0 1^d2 0 ... 0 1^dn 0 1^a 0 1^b 0 1 B> 0^inf   (ds top digit first, d1 >= 1 or n = 0)

A "shape" is (state, suffix): the head is in `state` on the blank right of the word, and the word ends with
`suffix` (parent: 'B', '01').  Everything left of the suffix is parsed as runs of 1s separated by single 0s:
ds..., a, b.  Leading zero digits merge into the blank.

  run_next(tm, ds, a, b)       literal simulation from K(ds;a;b) to the next K-shape configuration
                               -> ('K', steps, (ds, a, b)) | ('HALT', steps, (state, sym), sim) | ('TIMEOUT', steps)
  parent_predict(ds, a, b, r4) the parent's rules R1-R4 (r4: function b -> (ds, a, b) for the blank reset)
  grid(...)                    standard test grid (digits 0-3, up to 3 digits, a 0-3, b 1-5, long zero blocks)

CLI:  python kfam.py TM [N]      -> literal run from the blank tape, printing each K configuration
      python kfam.py TM ds a b   -> one successor, e.g.  python kfam.py TM 1,0,0 0 2
"""
import sys
import itertools
from tmlit import Sim, ST

SHAPE = ['B', '01']   # mutable: set_shape(state, suffix) switches the family shape for every tool

# Digit encoding (unit, separator): a digit d is unit^d, digits are separated by the separator. The default
# ('1', '0') is the parent's; BB_KENC=unit,sep (e.g. "10,11") generalizes it for scans of other machines.
# Units must start with '1' so leading blank cells stay unambiguous.
import os as _os
ENC = tuple(_os.environ.get('BB_KENC', '1,0').split(','))


def parse_runs(word):
    """Parse word = unit^d1 sep unit^d2 sep ... sep unit^dn (right to left, greedy); None if it does not parse."""
    u, sep = ENC
    runs = []
    w = word
    while True:
        k = 0
        while w.endswith(u):
            w = w[:-len(u)]
            k += 1
        runs.append(k)
        if not w or set(w) == {'0'}:
            break
        if not w.endswith(sep):
            return None
        w = w[:-len(sep)]
        if not w or set(w) == {'0'}:
            runs.append(0)
            break
    runs.reverse()
    return runs


def kword(ds, a, b, suffix=None):
    suffix = SHAPE[1] if suffix is None else suffix
    u, sep = ENC
    w = ''
    for d in ds:
        w += u * d + sep
    w += u * a + sep + u * b + suffix     # parent: ... 1^a 0 1^b 0 1
    return w.lstrip('0')


def kstart(tm, ds, a, b, shape=None):
    shape = shape or SHAPE
    w = kword(ds, a, b, shape[1])
    return Sim.from_word(tm, '0' * 4 + w + '0', 4 + len(w), shape[0], size=1 << 16)


def parse_at(s, shape=None):
    """If the simulator is in K shape return (ds, a, b) else None."""
    shape = shape or SHAPE
    q, suf = shape
    t = s.tape
    p = s.pos
    if ST[s.state] != q or t[p] != 0:
        return None
    n = len(suf)
    if t[p - 1] != int(suf[-1]):
        return None
    if p < s.hi and any(t[p + 1:s.hi + 1]):   # everything right of the head must be blank
        return None
    for i, c in enumerate(suf):
        if t[p - n + i] != int(c):
            return None
    lo = s.lo
    while lo < p and t[lo] == 0:
        lo += 1
    if ENC != ('1', '0'):
        word = ''.join(str(x) for x in t[lo:p - n])
        runs = parse_runs(word)
        if runs is None or len(runs) < 2:
            return None
        ds = runs[:-2]
        if ds and ds[0] == 0:
            return None
        return (tuple(ds), runs[-2], runs[-1])
    runs = []
    cur = 0
    i = p - n - 1
    while i >= lo:
        if t[i] == 1:
            cur += 1
        else:
            runs.append(cur)
            cur = 0
        i -= 1
    runs.append(cur)
    runs.reverse()
    if len(runs) < 2:
        return None
    ds = runs[:-2]
    if ds and ds[0] == 0:
        return None
    return (tuple(ds), runs[-2], runs[-1])


def run_from(s, N=10 ** 7, shape=None):
    start = s.steps
    while s.steps - start < N:
        if not s.step():
            return ('HALT', s.steps, (ST[s.last[0]], s.last[1]), s)
        r = parse_at(s, shape)
        if r is not None:
            return ('K', s.steps, r)
    return ('TIMEOUT', s.steps)


def run_next(tm, ds, a, b, N=10 ** 7, shape=None):
    return run_from(kstart(tm, ds, a, b, shape), N, shape)


def trailing_zeros(ds):
    k = 0
    while k < len(ds) and ds[len(ds) - 1 - k] == 0:
        k += 1
    return k


def strip(ds):
    ds = list(ds)
    while ds and ds[0] == 0:
        ds = ds[1:]
    return tuple(ds)


def parent_predict(ds, a, b, r4=lambda b: ((2,) + (1,) * (4 * b), 1, 1)):
    """Parent rules. Returns ('K', (ds,a,b)) or ('HALT',) or None (not predicted)."""
    ds = list(ds)
    if a >= 1:
        if not ds and a == 1:
            return ('K', r4(4 * b + 4))
        return ('K', (tuple(ds), a - 1, 4 * b + 4))
    k = trailing_zeros(ds)
    if k == len(ds):
        return ('K', r4(b))
    i = len(ds) - 1 - k
    if k == 0:
        ds[-1] -= 1
        return ('K', (strip(ds), 4 * b + 3, 1))
    if k <= 4 * b:
        ds[i] -= 1
        ds = ds[:i + 1] + [4 * b + 3 - k] + [1] * (k - 1)
        return ('K', (strip(ds), 1, 1))
    if k == 4 * b + 1:
        return ('HALT',)
    return None


def kind_of(ds, a, b):
    if a >= 1:
        return 'R1'
    k = trailing_zeros(ds)
    if k == len(ds):
        return 'R4'
    if k == 0:
        return 'R2'
    if k <= 4 * b:
        return 'R3'
    if k == 4 * b + 1:
        return 'HALT?'
    return 'R3big'


def grid(maxdig=3, maxval=3, maxa=3, maxb=5, long_b=3, long_extra=4):
    cases = []
    for n in range(0, maxdig + 1):
        for ds in itertools.product(range(0, maxval + 1), repeat=n):
            if ds and ds[0] == 0:
                continue
            for a in range(0, maxa + 1):
                for b in range(1, maxb + 1):
                    cases.append((ds, a, b))
    for b in range(1, long_b + 1):
        for k in range(1, 4 * b + long_extra + 1):
            for y in (1, 2):
                cases.append(((1, y) + (0,) * k, 0, b))
    return cases


def show(f):
    ds, a, b = f
    if len(ds) > 12:
        s = ','.join(map(str, ds[:6])) + ',...(%d digits)' % len(ds)
    else:
        s = ','.join(map(str, ds))
    return 'K(%s; %s; %s)' % (s, a, b)


def main():
    tm = sys.argv[1]
    if len(sys.argv) >= 5:
        ds = tuple(int(x) for x in sys.argv[2].split(',') if x not in ('', '-'))
        a, b = int(sys.argv[3]), int(sys.argv[4])
        r = run_next(tm, ds, a, b)
        if r[0] == 'K':
            print(show((ds, a, b)), '->', show(r[2]), 'in', r[1], 'steps')
        else:
            print(show((ds, a, b)), '->', r[:3])
        return
    N = int(sys.argv[2]) if len(sys.argv) > 2 else 10 ** 6
    s = Sim(tm)
    last = 0
    while s.steps < N:
        r = run_from(s, N - s.steps)
        if r[0] != 'K':
            print(r[:3], s.runs() if r[0] == 'HALT' else '')
            break
        print('step %d: %s  [+%d]' % (r[1], show(r[2]), r[1] - last))
        last = r[1]


if __name__ == '__main__':
    main()


def set_shape(state, suffix):
    """Switch the configuration shape used by all K-family tools, e.g. set_shape('F', '0') for
    0^inf 1^d1 0 ... 1^dn 0 1^a 0 1^b 0 F> 0^inf."""
    SHAPE[0] = state
    SHAPE[1] = suffix
