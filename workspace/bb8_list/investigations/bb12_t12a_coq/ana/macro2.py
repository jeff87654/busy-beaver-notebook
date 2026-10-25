"""macro2.py: B-form macro run of T12a from the round-1 end Bf (FarE k) (1^w ++ [0]) f.
CLR outputs that are huge get representatives from a per-index list (default base)."""
import sys, re, json
from bsim import *
CAP = 10**7

def U(n, A):
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

def comp(tk):
    return re.sub(r'((?:3 2 0 ){2,})', lambda m: '(3 2 0)^%d ' % (len(m.group(1).split()) // 3), ' ' + tk + ' ').strip()

class Run:
    def __init__(self, reps=None, base=40, verbose=True, stop_after=None):
        self.reps = dict(reps or {}); self.base = base; self.nclr = 0; self.verbose = verbose
        self.events = []; self.stop_after = stop_after
    def clr(self, word):
        toks = parse_tail(word)
        A = toks[0][1]; assert toks[1][1] == 0
        ts = toks[2:]
        n = 0
        while n < len(ts) and ts[n][1] == 1: n += 1
        if n < len(ts) and ts[n][1] >= 3 and (n == 0 or A % 3 == 1):
            st, X = ts[n]; d = X // 3
            v = iterU(d, n, A)
            kind = 'exact'
            if v is None:
                v = self.reps.get(self.nclr, self.base); kind = 'rep#%d' % self.nclr
                if n == 0: kind += '!depth0'
            self.nclr += 1
            if self.verbose: print('   CLR depth %d token %d A=%d -> %d (%s)' % (n, X, A, v, kind))
            return word[:st] + D(X % 3) + D(1) * n + D(0) + D(v)
        return None
    def go(self, word, head, q, nmax=100000, maxsteps=10**9):
        r = run_lit(word, head, q, maxsteps=maxsteps)
        ev = 0; prev = None
        while True:
            if r[0] != 'B':
                if self.verbose: print('END', r[0], r[1], 'steps', r[2])
                self.events.append(dict(inp=prev, out=None, end=r[:3]))
                return r
            word = r[1]
            if prev is not None:
                self.events.append(dict(inp=prev, out=word, steps=r[2], reads={'%s%d' % k: v for k, v in r[3].items() if k[0] in 'JKL'}))
            while True:
                w2 = self.clr(word)
                if w2 is None: break
                word = w2
            far, tk = fmt_word(word)
            ev += 1
            if self.verbose: print('B%03d far=%s..(%d) | %s' % (ev, far[-40:], len(far), comp(tk)[:300]), flush=True)
            prev = word
            if ev >= nmax or (self.stop_after and self.stop_after(word, ev)): return ('STOP', word)
            r = run_lit(word, len(word), 'H', maxsteps=maxsteps)

def bform(far, toks_ff, A):
    """far bits + tokens farthest-first + D0 D(A)"""
    return far + ''.join(D(m) for m in toks_ff) + D(0) + D(A)

def r1end(k, w, f):
    return bform(fare(k), [0] + [1] * w, f)

if __name__ == '__main__':
    k, w, f = map(int, sys.argv[1:4])
    reps = json.loads(sys.argv[4]) if len(sys.argv) > 4 else {}
    reps = {int(a): b for a, b in reps.items()}
    nmax = int(sys.argv[5]) if len(sys.argv) > 5 else 100000
    R = Run(reps)
    wd = r1end(k, w, f)
    R.go(wd, len(wd), 'H', nmax=nmax)
