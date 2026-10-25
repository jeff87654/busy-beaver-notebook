"""Ordered-fake event simulator (discovery tool).  Standard dynamics in macro form (esim2-style), specials literal.
Every deep clearing output gets the next value from a FAKE list (given in the order the clearings happen), so the size
order of the accumulators can be chosen.  Tokens are printed raw; fake values F_i are printed as 'F<i>+c' when close.
   osim.py LIST:A F1,F2,...  [MAXSPEC]"""
import sys
from fw import *
from hs import literal_next
from btrace import parse_list

FAKES = []
PLACE = 999997   # placeholder for intermediate deep values inside one jump (= 1 mod 3)
used = []


def nextfake():
    v = FAKES[len(used)]
    used.append(v)
    return v


def lab(v):
    best = None
    for i, f in enumerate(used):
        for k in (1, 2):
            c = v - k * f
            if abs(c) <= 60:
                s = ('%sF%d%+d' % ('' if k == 1 else '2', i + 1, c)) if c else ('%sF%d' % ('' if k == 1 else '2', i + 1))
                if best is None or abs(c) < best[0]:
                    best = (abs(c), s)
    return best[1] if best else str(v)


def comp(items):
    # compress runs of a repeated block of length 1..4
    out = []
    i = 0
    n = len(items)
    while i < n:
        best = (1, 1)
        for p in (1, 2, 3, 4):
            if i + p > n:
                break
            k = 1
            while i + (k + 1) * p <= n and items[i + k * p:i + (k + 1) * p] == items[i:i + p]:
                k += 1
            if k > 1 and k * p > best[0] * best[1]:
                best = (p, k)
        p, k = best
        out.append((items[i:i + p], k))
        i += p * k
    return out


def tl(x):
    return ('D%d' % x) if x < 1000 else 'D[%s]' % lab(x)


def flab(L, A):
    out = []
    for blk, k in comp(L):
        t = ' '.join(tl(x) for x in blk)
        out.append(t if k == 1 else ('%s^%d' % (t, k) if len(blk) == 1 else '(%s)^%d' % (t, k)))
    return '[%s | %s]' % (' '.join(out), str(A) if A < 1000 else lab(A))


def macro(L, A, log):
    t = L[-1] if L else None
    if t is None:
        return None
    if t >= 3:
        n = t // 3
        M = L[:-1] + [t % 3]
        if n <= 6 and A < 1000:
            A2 = (2 ** n) * (A + 8) - 8
            if A2 < 1000:
                return M, A2
        log.append('R1run(%s, %d units)' % ('D%d' % t if t < 1000 else lab(t), n))
        return M, PLACE
    if t == 1:
        j = len(L) - 1
        while j >= 0 and L[j] == 1:
            j -= 1
        if j < 0 or L[j] < 3:
            return None
        if A % 3 == 1 and j <= len(L) - 2:
            M = list(L); M[j] = L[j] % 3
            log.append('CLR(%s@d%d->D%d)' % ('D%d' % L[j] if L[j] < 1000 else 'D[' + lab(L[j]) + ']', len(L) - 1 - j, L[j] % 3))
            return M, PLACE
        M = list(L); M[j] -= 3; M[j + 1] = A + 3
        return M, 4
    return None


def run(L, A, maxspec=60, log=print):
    nspec = 0
    while nspec < maxspec:
        tags = []
        while True:
            mv = macro(L, A, tags)
            if mv is None:
                break
            L, A = mv
        if A == PLACE:
            A = nextfake()
        if tags:
            sh = tags if len(tags) <= 8 else tags[:4] + ['...%d ops...' % (len(tags) - 8)] + tags[-4:]
            log('   jump: ' + ' '.join(sh) + '  -> ' + flab(L, A))
        kind, L2, A2, st, evs = literal_next(L, A, 10 ** 12)
        if kind != 'B':
            log('END %s at %s after %s steps: %s' % (kind, flab(L, A), st, show(L2)[:300] if isinstance(L2, dict) else L2))
            return kind
        log('SPECIAL %s -> %s  (%d st, %d E0)' % (flab(L, A), flab(L2, A2), st, len(evs)))
        L, A = L2, A2
        nspec += 1
    return 'MAXSPEC'


if __name__ == '__main__':
    _ts, A = sys.argv[1].rsplit(':', 1)
    FAKES[:] = [int(x) for x in sys.argv[2].split(',')]
    run(parse_list(_ts), int(A), int(sys.argv[3]) if len(sys.argv) > 3 else 60, log=lambda s: print(s, flush=True))
