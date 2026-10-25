"""Hybrid follower for n1 with a FAR region: config (far, L, A) = tape far + D(L1)..D(Ln) D0 D(A), head right of it in
state H.  far is an arbitrary bit string ending in a 00 run (or empty).  Standard R1/R2 act only on L (verified rules);
everything else is literal (sim.exe, stop at the next relaxed B-form 'BgH').  Deep clearing outputs are fakes.
   n1sim.py B F1,F2,...  [MAXSPEC]"""
import sys, hashlib
from fw import *
from osim import comp

FAKES = []
used = []
PLACE = 999997
_S = None


def srv():
    global _S
    if _S is None:
        _S = Server(M10, 'BgH,E0', 10 ** 9)
    return _S


def word3(far, L, A):
    w = far + ''.join(D(t) for t in L) + D(0) + D(A)
    return w, len(w), 'H'


def parse3(word, rel):
    if rel == len(word) - 1 and word[-1] == '0':
        word = word[:-1]
    it = tok(word)
    # last zero-run item
    last = -1
    for i, x in enumerate(it):
        if not isinstance(x, int):
            last = i
    pos = 0
    for x in it[:last + 1]:
        pos += (2 * x + 1) if isinstance(x, int) else int(x[1:])
    far = word[:pos]
    rest = it[last + 1:]
    assert all(isinstance(x, int) for x in rest) and len(rest) >= 2 and rest[-2] == 0, (rest[-4:],)
    return far, rest[:-2], rest[-1]


def literal(far, L, A, maxsteps=10 ** 12):
    w, h, q = word3(far, L, A)
    evs = []
    for x in srv().job(w, h, q, maxsteps):
        if x['kind'] == 'BF':
            f2, L2, A2 = parse3(x['word'], x['rel'])
            return 'B', (f2, L2, A2), x['step'], evs
        if x['kind'] == 'EV':
            evs.append(x)
            continue
        return x['kind'], x, x.get('step'), evs
    return 'NONE', None, None, evs


def nextfake():
    v = FAKES[len(used)]
    used.append(v)
    return v


def macro(L, A, log):
    """one standard macro move on L (never touching far) or None."""
    if not L:
        return None
    t = L[-1]
    if t >= 3:
        n = t // 3
        M = L[:-1] + [t % 3]
        if n <= 6 and A < 1000:
            A2 = (2 ** n) * (A + 8) - 8
            if A2 < 1000:
                return M, A2
        log.append('R1run(%d units)' % n)
        return M, PLACE
    if t == 1:
        j = len(L) - 1
        while j >= 0 and L[j] == 1:
            j -= 1
        if j < 0 or L[j] < 3:
            return None
        if A % 3 == 1 and j <= len(L) - 2:
            M = list(L); M[j] = L[j] % 3
            log.append('CLR(%s@d%d->D%d)' % (L[j] if L[j] < 1000 else 'F', len(L) - 1 - j, L[j] % 3))
            return M, PLACE
        M = list(L); M[j] -= 3; M[j + 1] = A + 3
        return M, 4
    return None


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


def flab(far, L, A):
    out = []
    for blk, k in comp(L):
        t = ' '.join(('D%d' % x) if x < 1000 else 'D[%s]' % lab(x) for x in blk)
        out.append(t if k == 1 else ('%s^%d' % (t, k) if len(blk) == 1 else '(%s)^%d' % (t, k)))
    fh = hashlib.md5(far.encode()).hexdigest()[:6] if far else '-'
    return 'far(%d bits,%s) [%s | %s]' % (len(far), fh, ' '.join(out), str(A) if A < 1000 else lab(A))


def run(B, fakes, maxspec=400, log=print, start=None):
    FAKES[:] = fakes; used[:] = []
    far, L, A = start if start else ('', [1] * 36, 6 * B + 4)
    sig = []
    for _ in range(maxspec):
        tags = []
        while True:
            mv = macro(L, A, tags)
            if mv is None:
                break
            L, A = mv
        if A == PLACE:
            A = nextfake()
        if tags:
            sig.append('J')
            log('   jump: %s  -> %s' % (' '.join(tags[:2] + (['..%d..' % (len(tags) - 4)] if len(tags) > 4 else []) + tags[-2:] if len(tags) > 4 else tags), flab(far, L, A)))
        kind, res, st, evs = literal(far, L, A)
        if kind != 'B':
            log('END %s: %s' % (kind, show(res)[:300] if isinstance(res, dict) else res))
            return sig, kind, res
        sig.append('S')
        f2, L2, A2 = res
        log('SPECIAL %s -> %s  (%s st, %d E0)' % (flab(far, L, A), flab(f2, L2, A2), st, len(evs)))
        far, L, A = f2, L2, A2
    return sig, 'MAXSPEC', None


if __name__ == '__main__':
    B = int(sys.argv[1]); fk = [int(x) for x in sys.argv[2].split(',')]
    run(B, fk, int(sys.argv[3]) if len(sys.argv) > 3 else 400, log=lambda s: print(s, flush=True))
