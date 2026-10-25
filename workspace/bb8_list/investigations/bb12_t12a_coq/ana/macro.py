"""macro.py: B-form macro run of T12a: CLR jumps (with representative accumulators) + literal events."""
import sys
from bsim import *
sys.setrecursionlimit(10000)
CAP = 10**7
M = 5040
THR = [40]      # representative base
def tower_mod(m):
    from sympy.ntheory import reduced_totient
    if m == 1: return 0
    lam = int(reduced_totient(m))  # noqa
    e = tower_mod(lam)
    return pow(2, e + lam * 64, m)
TM_ = tower_mod(M)
STABLE = (3 * TM_ - 8) % M        # deep clear output class
def rep(res):
    b = THR[0]
    return b + ((res - b) % M)
def U(n, A):
    """exact U n A or None if > CAP"""
    if n == 0:
        v = 2 * A + 8
        return v if v < CAP else None
    x = 4
    for _ in range(A // 3 + 1):
        x = U(n - 1, x)
        if x is None: return None
    return x
def iterU(d, n, A):
    x = A
    for _ in range(d):
        x = U(n, x)
        if x is None: return None
    return x

def step(word, log):
    toks = parse_tail(word)
    A = toks[0][1]
    assert toks[1][1] == 0
    ts = toks[2:]
    n = 0
    while n < len(ts) and ts[n][1] == 1: n += 1
    if n < len(ts) and ts[n][1] >= 3 and (n == 0 or A % 3 == 1):
        st, X = ts[n]
        d = X // 3
        v = iterU(d, n, A)
        kind = 'exact'
        if v is None:
            if n >= 1:
                v = rep(STABLE); kind = 'deep'
            else:
                v = rep((pow(2, d, M) * (A + 8) - 8) % M) if d < 64 else rep(STABLE); kind = 'R1big' if d < 64 else 'R1huge?'
        log.append(('CLR', n, X, A, v, kind))
        return word[:st] + D(X % 3) + D(1) * n + D(0) + D(v)
    return None

def comp(tk):
    import re
    return re.sub(r'((?:3 2 0 ){2,})', lambda m: '(3 2 0)^%d ' % (len(m.group(1).split()) // 3), tk + ' ').strip()

def go(word, head, q, nmax=100000, verbose=True, maxsteps=10**8):
    r = run_lit(word, head, q, maxsteps=maxsteps)
    ev = 0
    out = []
    while True:
        if r[0] != 'B':
            out.append(("END", r[:3]))
            if verbose: print('END', r[0], r[1], 'steps', r[2], 'reads', {k: v for k, v in r[-1].items() if k[0] in 'JKL'})
            return out
        word = r[1]
        while True:
            log = []
            w2 = step(word, log)
            if w2 is None: break
            if verbose:
                c = log[0]; print('   CLR depth %d token %d A=%d -> %d (%s)' % c[1:])
            out.append(log[0]); word = w2
        far, tk = fmt_word(word)
        ev += 1
        if verbose: print('B%03d far=%s..(%d) | %s' % (ev, far[-40:], len(far), comp(tk)[:300]))
        out.append(('B', word))
        if ev >= nmax: return out
        r = run_lit(word, len(word), 'H', maxsteps=maxsteps)
        if r[0] == 'B' and verbose:
            print('     event: %d steps, new reads %s' % (r[2], {k: v for k, v in r[3].items() if k[0] in 'JKL'}))
        out.append(('EV', r[2] if r[0] == 'B' else None))

if __name__ == '__main__':
    k = int(sys.argv[1]); n = int(sys.argv[2]); R = int(sys.argv[3])
    if len(sys.argv) > 4: THR[0] = int(sys.argv[4])
    print('STABLE', STABLE, 'rep', rep(STABLE))
    w = fare(k) + ''.join(D(m) for m in [0] + [1] * n + [1, R]) + '1010'
    go(w, len(w), 'G')
