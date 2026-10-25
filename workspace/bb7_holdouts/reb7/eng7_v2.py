"""eng7.py (v2): residue-faithful evaluator of fitted K-level rules (reb7).

Levels (generic spec: list L(x) for positions len(L)..1, start F0^{A(x)}(B(x)); value = clear(L(x)) of the start):
  ('U',0) = F0 (one D step)
  ('U',1): L = [], A = A2, B = B2                     (decrement the last digit, run a down)
  ('U',j>=2): borrow over k = j-1 zeros: L = L_k(x), A, B = a_k, b_k
  ('W',i>=1): marker borrow with i zero digits (P nonempty): L of length i-1, A, B from the MB fit
  clear([l_1..l_k]) = U_k^{l_1} o ... o U_1^{l_k}
Exhaustion value of K(ds; a; b) (ds top-first): V = U_n^{d_1} o ... o U_1^{d_n} o F0^a (b); with a marker the
staircase W_1 o ... o W_n follows (n = len(ds)), then the true exhaustion E0.

Numbers: exact Python ints below LIM, else Huge(r) = a number >= LIM known mod Q (Huge.mod set when it is only
known mod a divisor of Q). Every count >= LIM exceeds every pre-period (< Q + 100 << LIM), so a level on huge
inputs is a function of the residue (a table mod Q) whenever the cycle lengths involved divide Q (checked;
violations go to self.flags).
U tables are eventually periodic in the level index: state = (tables of the last levels, G, x1*k mod lcm(cycles))
repeats exactly -> period (mu, P); deeper levels are mapped into [mu, mu + P). Same for W.
"""
import math
import numpy as np

LIM = 10 ** 15


class Huge:
    __slots__ = ('r', 'mod')

    def __init__(self, r, mod=None):
        self.r = r
        self.mod = mod

    def __repr__(self):
        return 'H%d' % self.r if not self.mod else 'H%d/%d' % (self.r, self.mod)

    def __eq__(self, o):
        return isinstance(o, Huge) and o.r == self.r and o.mod == self.mod

    def __hash__(self):
        return hash(('H', self.r, self.mod))


class EngError(Exception):
    pass


def pattern_rule(p, k, fitted):
    """rule for a borrow-like level with k positions below (k >= 1) from the fitted table / pattern"""
    if k in fitted:
        x = fitted[k]
        return [tuple(e) for e in x['L']], tuple(x['a']), tuple(x['b'])
    nmid = k - 1 - len(p['head']) - len(p['end'])
    if nmid < 0:
        raise EngError('pattern undefined at k=%d' % k)
    L = [(p['m'], p['x0'] + p['x1'] * k)] + [(0, v) for v in p['head']] + [(0, p['mid'])] * nmid + \
        [(0, v) for v in p['end']]
    return L, tuple(p['a']), tuple(p['b'])


def borrow_rule(R, k):
    return pattern_rule(R['Bpat'], k, R['B'])


class Eng:
    def __init__(self, R, Q=20160, JMAX=400):
        self.R, self.Q, self.JMAX = R, Q, JMAX
        self.flags = []
        self.precond = []
        self.memo = {}
        self.tab = {}
        self.const = {}
        self.orbits = {}
        self.desc = {}
        self.Kc = {}
        self.period = {}
        self.lams = {'U': set(), 'W': set()}
        self.calls = 0
        self.thr, self.thr_lin = self._thresholds(R.get('smallB', {}))
        self.thrW, self.thrW_lin = self._thresholds(R.get('smallMB') or {})

    # ----------------------------------------------------------------------------------------- numbers
    def mk(self, v):
        if isinstance(v, Huge):
            return v
        if v < 0:
            self.precond.append('negative %d' % v)
            raise EngError('negative value')
        return v if v < LIM else Huge(v % self.Q)

    def affv(self, f, x):
        m, c = f
        if isinstance(x, Huge):
            if m == 0:
                return self.mk(c)
            if m < 0:
                raise EngError('negative slope on huge value')
            if x.mod:
                return Huge((m * x.r + c) % x.mod, x.mod)
            return Huge((m * x.r + c) % self.Q)
        return self.mk(m * x + c)

    def res(self, x):
        return x.r if isinstance(x, Huge) else x % self.Q

    @staticmethod
    def _thresholds(small):
        thr = {}
        for k, lst in small.items():
            bad = [b for b, *_ in lst]
            thr[int(k)] = (max(bad) + 1) if bad else 0
        ks = sorted(thr)
        lin = None
        if len(ks) >= 2:
            k1, k2 = ks[-2], ks[-1]
            sl = max(0, (thr[k2] - thr[k1]) // max(1, k2 - k1))
            lin = (sl, thr[k2] - sl * k2)
        return thr, lin

    def threshold(self, kind, k):
        thr, lin = (self.thr, self.thr_lin) if kind == 'U' else (self.thrW, self.thrW_lin)
        if k in thr:
            return thr[k]
        if lin is None:
            return 3 * k + 6
        return max(0, lin[0] * k + lin[1] + (1 if lin[0] else 0))

    # ----------------------------------------------------------------------------------------- specs
    def spec(self, lev):
        kind, j = lev
        R = self.R
        if kind == 'U':
            if j == 1:
                return [], tuple(R['A2']), tuple(R['B2'])
            return borrow_rule(R, j - 1)
        if j == 1:
            x = R['MB'][1]
            return [], tuple(x['a']), tuple(x['b'])
        return pattern_rule(R['MBpat'], j - 1, {n - 1: v for n, v in R['MB'].items() if n >= 2})

    # ----------------------------------------------------------------------------------------- level 0 (F0)
    def f0pow(self, n, x):
        m, c = self.R['F0']
        if n == 0:
            return x
        if m == 0:
            return self.mk(c)
        if m == 1:
            if isinstance(n, Huge) or isinstance(x, Huge):
                if (isinstance(n, Huge) and n.mod) or (isinstance(x, Huge) and x.mod):
                    self.flags.append('reduced modulus in an additive step')
                return Huge((self.res(x) + c * self.res(n)) % self.Q)
            return self.mk(x + c * n)
        if not isinstance(n, Huge) and not isinstance(x, Huge) and n * m.bit_length() < 60:
            v = x
            for _ in range(n):
                v = m * v + c
            return self.mk(v)
        if not isinstance(n, Huge):
            if isinstance(x, Huge) and x.mod:
                self.flags.append('reduced modulus in F0 power')
            Mq = self.Q * (m - 1)
            T = (pow(m, n, Mq) * (self.res(x) * (m - 1) + c) - c) % Mq
            return Huge((T // (m - 1)) % self.Q)
        vals, mu, lam = self.orbit(('U', 0), x)
        return vals[self.index(n, mu, lam, len(vals))]

    # ----------------------------------------------------------------------------------------- level reps
    def rep(self, lev):
        kind, j = lev
        if j <= self.JMAX:
            return lev
        if kind not in self.period:
            self.find_period(kind)
        mu, P = self.period[kind]
        return (kind, mu + (j - mu) % P)

    # ----------------------------------------------------------------------------------------- application
    def U(self, j, x):
        return self.apply(('U', j), x)

    def apply(self, lev, x):
        kind, j = lev
        if kind == 'U' and j == 0:
            return self.affv(self.R['F0'], x)
        lev = self.rep(lev)
        kind, j = lev
        if isinstance(x, Huge):
            self.table(lev)
            if lev in self.const:
                return self.const[lev]
            if x.mod:
                self.flags.append('table lookup on a reduced-modulus value')
            return Huge(int(self.tab[lev][x.r % self.Q]))
        key = (lev, x)
        if key in self.memo:
            return self.memo[key]
        self.calls += 1
        if self.calls > 3000000:
            raise EngError('evaluation budget')
        L, fa, fb = self.spec(lev)
        k = len(L)
        if kind == 'U' and j == 1:
            exc = dict((bb, ab) for bb, ab in (self.R.get('excR2') or []))
            if x in exc:
                v = self.f0pow(self.mk(exc[x][0]), self.mk(exc[x][1]))
                self.memo[key] = v
                return v
        if (kind == 'U' and j >= 2) or kind == 'W':
            kk = k if kind == 'U' else j
            th = self.threshold(kind, kk)
            if x < th:
                self.precond.append('%s%d at exact b=%d (< fitted threshold %d)' % (kind, j, x, th))
                sm = (self.R['smallB'] if kind == 'U' else (self.R.get('smallMB') or {})).get(kk, [])
                lit = [e for e in sm if e[0] == x]
                if lit and lit[0][1] == 'H':
                    raise EngError('HALT: %s level %d at exact b=%d halts' % (kind, j, x))
                raise EngError('small-b %s level %d at b=%d outside the fitted rule (%s)' % (kind, j, x, lit[:1]))
        v = self.f0pow(self.affv(fa, x), self.affv(fb, x))
        for i in range(1, k + 1):
            v = self.pow(i, self.affv(L[k - i], x), v)
        self.memo[key] = v
        return v

    def index(self, n, mu, lam, ln):
        if isinstance(n, Huge):
            md = n.mod or self.Q
            if md % lam:
                self.flags.append('cycle %d does not divide modulus %d' % (lam, md))
            return mu + ((n.r - mu) % lam)
        if n < ln:
            return n
        return mu + ((n - mu) % lam)

    def level_desc(self, j):
        """structural form of U_j: ('aff', M, C) (x -> M x + C, C exact or Huge; M = 0: constant) or ('gen',)"""
        j = self.rep(('U', j))[1]
        if j in self.desc:
            return self.desc[j]
        R = self.R
        m1, c1 = R['F0']
        d = ('gen',)
        if j == 1:
            if not R.get('excR2'):
                mA, cA = R['A2']
                mB, cB = R['B2']
                if m1 == 0 and (mA > 0 or cA > 0):
                    d = ('aff', 0, self.mk(c1))
                elif m1 == 1:
                    d = ('aff', mB + c1 * mA, self.mk(cB + c1 * cA))
        else:
            L, fa, fb = self.spec(('U', j))
            k = len(L)
            if fa[0] == 0 and fb[0] == 0 and all(e[0] == 0 for e in L[1:]) and L[0][0] >= 0:
                pd = self.level_desc(k)
                mt, ct = L[0]
                if pd[0] == 'aff' and pd[1] == 0:
                    d = ('aff', 0, pd[2]) if (mt > 0 or ct > 0) else ('gen',)
                elif pd[0] == 'aff' and pd[1] == 1 and not isinstance(pd[2], Huge):
                    th = self.threshold('U', k)
                    if th == 0:
                        K = self.Kval(('U', j))
                        C = pd[2]
                        if isinstance(K, Huge):
                            d = ('aff', C * mt, Huge((K.r + C * ct) % self.Q))
                        else:
                            d = ('aff', C * mt, self.mk(K + C * ct))
        self.desc[j] = d
        return d

    def pow(self, j, n, x):
        """U_j^n(x)"""
        if n == 0:
            return x
        if j == 0:
            return self.f0pow(n, x)
        lev = self.rep(('U', j))
        j = lev[1]
        d = self.level_desc(j)
        if d[0] == 'aff' and d[1] == 0:
            return d[2]
        if d[0] == 'aff' and d[1] == 1:
            C = d[2]
            if (isinstance(n, Huge) and n.mod) or (isinstance(x, Huge) and x.mod):
                self.flags.append('reduced modulus in an additive level')
            if isinstance(n, Huge) or isinstance(x, Huge) or isinstance(C, Huge):
                return Huge((self.res(x) + self.res(C) * self.res(n)) % self.Q)
            return self.mk(x + C * n)
        if not isinstance(n, Huge) and n <= 3:
            v = x
            for _ in range(n):
                v = self.apply(lev, v)
            return v
        vals, mu, lam = self.orbit(lev, x)
        return vals[self.index(n, mu, lam, len(vals))]

    def orbit(self, lev, x):
        key = (lev, x)
        if key in self.orbits:
            return self.orbits[key]
        vals = [x]
        seen = {}
        v = x
        if isinstance(v, Huge):
            seen[v.r] = 0
        exact_seen = {v: 0} if not isinstance(v, Huge) else {}
        mu = lam = None
        for i in range(1, 4 * self.Q + 400):
            v = self.apply(lev, v)
            if isinstance(v, Huge):
                if v.r in seen:
                    mu, lam = seen[v.r], i - seen[v.r]
                    break
                seen[v.r] = i
            else:
                if v in exact_seen:
                    mu, lam = exact_seen[v], i - exact_seen[v]
                    break
                exact_seen[v] = i
                if i == 3000:
                    raise EngError('slow exact orbit at level %s (additive level: counter?)' % (lev,))
            vals.append(v)
        if mu is None:
            raise EngError('no cycle at level %s' % (lev,))
        self.orbits[key] = (vals, mu, lam)
        return self.orbits[key]

    # ----------------------------------------------------------------------------------------- tables
    def table(self, lev):
        if lev in self.tab or lev in self.const:
            return
        Q = self.Q
        r = np.arange(Q, dtype=np.int64)
        kind, j = lev
        L, fa, fb = self.spec(lev)
        k = len(L)
        m1, c1 = self.R['F0']
        if k == 0:
            mA, cA = fa
            mB, cB = fb
            if mA == 0 and mB == 0:
                self.const[lev] = self.f0pow(self.mk(cA), self.mk(cB))
                return
            if m1 == 1:
                self.tab[lev] = ((mB * r + cB + c1 * (mA * r + cA)) % Q).astype(np.int32)
                return
            if m1 == 0:
                self.const[lev] = self.mk(c1)
                return
            if mB != 0:
                raise EngError('b-dependent start with multiplicative F0: unsupported (%s)' % (lev,))
            if mA == 0:
                self.const[lev] = self.f0pow(self.mk(cA), self.mk(cB))
                return
            vals, mu, lam = self.orbit(('U', 0), self.mk(cB))
            if Q % lam:
                self.flags.append('%s cycle %d does not divide Q' % (lev, lam))
            n = (mA * r + cA) % Q
            idx = mu + (n - mu) % lam
            arr = np.array([self.res(v) for v in vals], dtype=np.int64)
            self.tab[lev] = arr[idx].astype(np.int32)
            return
        if fa[0] != 0 or fb[0] != 0 or any(e[0] != 0 for e in L[1:]):
            raise EngError('level %s: b-dependent tail/a/b unsupported' % (lev,))
        K = self.Kval(lev)
        top = L[0]
        if top[0] == 0:
            self.const[lev] = self.pow(k, self.mk(top[1]), K)
            return
        if top[0] < 0:
            raise EngError('negative refill slope')
        n = (top[0] * r + top[1]) % Q
        d = self.level_desc(k)
        if d[0] == 'aff' and d[1] == 1:
            self.tab[lev] = ((self.res(K) + self.res(d[2]) * n) % Q).astype(np.int32)
            return
        if d[0] == 'aff' and d[1] == 0:
            self.const[lev] = d[2]
            return
        lk = self.rep(('U', k))
        self.table(lk)
        if lk in self.const:
            self.const[lev] = self.const[lk]
            return
        vals, mu, lam = self.orbit(lk, K)
        self.lams[kind].add(lam)
        if Q % lam:
            self.flags.append('%s cycle %d does not divide Q' % (lev, lam))
        idx = mu + (n - mu) % lam
        arr = np.array([self.res(v) for v in vals], dtype=np.int64)
        self.tab[lev] = arr[idx].astype(np.int32)

    def pat(self, kind):
        return self.R['Bpat'] if kind == 'U' else self.R['MBpat']

    def fitted_ks(self, kind):
        return set(self.R['B']) if kind == 'U' else set(n - 1 for n in self.R['MB'] if n >= 2)

    def Kval(self, lev):
        if lev in self.Kc:
            return self.Kc[lev]
        kind, j = lev
        L, fa, fb = self.spec(lev)
        k = len(L)
        p = self.pat(kind)
        if k in self.fitted_ks(kind) or k < p['k0'] + 3 or k - 1 - len(p['head']) <= len(p['end']) + 1:
            v = self.f0pow(self.mk(fa[1]), self.mk(fb[1]))
            for i in range(1, k):
                v = self.pow(i, self.mk(L[k - i][1]), v)
        else:
            v = self.G(kind, k)
            hl = len(p['head'])
            for idx in range(hl):
                pos = k - hl + idx
                v = self.pow(pos, self.mk(p['head'][hl - 1 - idx]), v)
        self.Kc[lev] = v
        return v

    def G(self, kind, k):
        key = ('G', kind, k)
        if key in self.Kc:
            return self.Kc[key]
        p = self.pat(kind)
        hl, el = len(p['head']), len(p['end'])
        top = k - 1 - hl
        if top <= el + 1 or k <= p['k0'] + 2 or (k in self.fitted_ks(kind)) or (k - 1 in self.fitted_ks(kind)):
            L, fa, fb = pattern_rule(p, k, {})
            v = self.f0pow(self.mk(p['a'][1]), self.mk(p['b'][1]))
            for i in range(1, top + 1):
                v = self.pow(i, self.mk(L[k - i][1]), v)
        else:
            v = self.pow(top, self.mk(p['mid']), self.G(kind, k - 1))
        self.Kc[key] = v
        return v

    def state_key(self, kind, j):
        if kind == 'W':
            p = self.pat('W')
            lev = ('W', j + 1)
            self.table(lev)
            tw = ('c', self.res(self.const[lev])) if lev in self.const else ('t', hash(self.tab[lev].tobytes()))
            g = self.G('W', j)
            M = 1
            for l in self.lams['U'] | self.lams['W']:
                M = M * l // math.gcd(M, l)
            return hash((self.state_key('U', j), tw, self.res(g), isinstance(g, Huge), (p['x1'] * j) % M, M))
        p = self.pat(kind)
        hl = len(p['head'])
        parts = []
        for i in range(j - hl - 2, j + 1):
            lev = ('U', i)
            self.table(lev)
            parts.append(('c', self.res(self.const[lev])) if lev in self.const else ('t', hash(self.tab[lev].tobytes())))
        if kind == 'W':
            lev = ('W', j + 1)
            self.table(lev)
            parts.append(('c', self.res(self.const[lev])) if lev in self.const else ('t', hash(self.tab[lev].tobytes())))
        g = self.G(kind, j)
        M = 1
        for l in self.lams['U'] | self.lams['W']:
            M = M * l // math.gcd(M, l)
        return hash((tuple(parts), self.res(g), isinstance(g, Huge), (p['x1'] * j) % M, M))

    def find_period(self, kind):
        """state at index j determines the levels above it; repeat at j and mu -> levels > mu periodic"""
        seen = {}
        p = self.pat(kind)
        fk = self.fitted_ks(kind)
        j0 = max(p['k0'] + 5, (max(fk) if fk else 0) + 3, len(p['head']) + 4)
        for j in range(j0, self.JMAX):
            key = self.state_key(kind, j)
            if key in seen:
                mu = seen[key]
                self.period[kind] = (mu + 1, j - mu)
                return
            seen[key] = j
        raise EngError('no %s level period up to %d' % (kind, self.JMAX))

    # ----------------------------------------------------------------------------------------- evaluation
    def value(self, ds, a, b):
        v = self.f0pow(self.mk(a), self.mk(b))
        n = len(ds)
        for i in range(1, n + 1):
            v = self.pow(i, self.mk(ds[n - i]), v)
        return v

    def value_struct(self, pre, mid, cnt, suf, a, b):
        """clear K(pre + mid^cnt + suf; a; b); cnt exact int or (residue, modulus)"""
        v = self.f0pow(a, b)
        ns = len(suf)
        for i in range(1, ns + 1):
            v = self.pow(i, self.mk(suf[ns - i]), v)
        if not isinstance(cnt, tuple):
            for i in range(ns + 1, ns + cnt + 1):
                v = self.pow(i, self.mk(mid), v)
            top0 = ns + cnt
            for i in range(1, len(pre) + 1):
                v = self.pow(top0 + i, self.mk(pre[len(pre) - i]), v)
            return v
        if 'U' not in self.period:
            self.find_period('U')
        mu, P = self.period['U']
        cr, cmod = cnt
        if mid == 0:
            Wc = v
        else:
            seen = {}
            Ws = []
            i = ns + 1
            W = v
            while True:
                if i > mu and isinstance(W, Huge):
                    key = (self.rep(('U', i)), W.r)
                    if key in seen:
                        i0 = seen[key]
                        PW = i - i0
                        break
                    seen[key] = i
                Ws.append(W)
                W = self.pow(i, self.mk(mid), W)
                i += 1
                if i > ns + 200000:
                    raise EngError('no mid-run period')
            t0 = i0 - (ns + 1)
            if cmod % PW:
                self.flags.append('mid-run period %d does not divide the count modulus %d' % (PW, cmod))
            t = t0 + (cr - t0) % PW
            Wc = Ws[t]
        if cmod % P:
            self.flags.append('level period %d does not divide the count modulus %d' % (P, cmod))
        v = Wc
        for i in range(1, len(pre) + 1):
            j = mu + ((ns + cr + i) - mu) % P
            v = self.pow(j, self.mk(pre[len(pre) - i]), v)
        return v

    def staircase(self, V, n):
        """W_1 o W_2 o ... o W_n (V); n exact int or (residue, modulus)"""
        if not isinstance(n, tuple):
            if n > 300000:
                raise EngError('staircase too long (%d)' % n)
            v = V
            for i in range(n, 0, -1):
                v = self.apply(('W', i), v)
            return v
        if 'U' not in self.period:
            self.find_period('U')
        if 'W' not in self.period:
            self.find_period('W')
        mu, P = self.period['W']
        mu = max(mu, self.period['U'][0] + 1)
        nr, nmod = n
        if nmod % P:
            self.flags.append('W period %d does not divide modulus %d' % (P, nmod))
        if not isinstance(V, Huge):
            raise EngError('staircase over a huge count from an exact value')
        r = (nr - mu) % P
        v = V
        for rr in range(r, 0, -1):
            v = self.apply(('W', mu + rr), v)
        order = [mu] + list(range(mu + P - 1, mu, -1))
        C = np.arange(self.Q, dtype=np.int64)
        for lv in order:
            lev = self.rep(('W', lv))
            self.table(lev)
            if lev in self.const:
                C = np.full(self.Q, self.res(self.const[lev]), dtype=np.int64)
                continue
            C = self.tab[lev][C].astype(np.int64)
        x = self.res(v)
        seen = {x: 0}
        seq = [x]
        while True:
            x = int(C[x])
            if x in seen:
                m0, lam = seen[x], len(seq) - seen[x]
                break
            seen[x] = len(seq)
            seq.append(x)
        qmod = nmod // P if nmod % P == 0 else 1
        if qmod % lam:
            self.flags.append('staircase block cycle %d vs count modulus %d' % (lam, qmod))
        qr = ((nr - mu - r) // P) % qmod
        idx = m0 + (qr - m0) % lam
        v = Huge(seq[idx])
        for lv in range(mu, 0, -1):
            v = self.apply(('W', lv), v)
        return v
