"""eng7.py: residue-faithful evaluator of fitted K-level rules (reb7).

Levels: U_0 = F0 (one D step), U_1(x) = F0^{A2(x)}(B2(x)) (decrement the last digit, run a down),
U_{k+1}(x) = clear(L_k(x)) (F0^{a_k}(b_k)) with clear([l_1..l_k]) = U_k^{l_1} o ... o U_1^{l_k}   (borrow over k zeros).
Exhaustion value of K(ds; a; b) (ds top-first): V = U_n^{d_1} o ... o U_1^{d_n} o F0^a (b).

Numbers: exact Python ints below LIM, else Huge(r) = a number >= LIM known mod Q. Every count >= LIM exceeds every
pre-period (pre-periods are < Q + 100 << LIM), so U_j on huge inputs is a function of the residue (a table mod Q)
whenever the cycle lengths involved divide Q (checked; violations go to self.flags).
Level tables are eventually periodic in the level index: state_k = (tables of the last p+1 levels, G_k, x1*k mod Q)
repeats exactly -> period (mu_L, P_L); deeper levels are mapped into [mu_L, mu_L + P_L).
"""
import numpy as np

LIM = 10 ** 15


class Huge:
    __slots__ = ('r', 'mod')

    def __init__(self, r, mod=None):
        self.r = r
        self.mod = mod          # None = known mod the engine's Q; else known only mod `mod` (a divisor of Q)

    def __repr__(self):
        return 'H%d' % self.r

    def __eq__(self, o):
        return isinstance(o, Huge) and o.r == self.r

    def __hash__(self):
        return hash(('H', self.r))


class EngError(Exception):
    pass


def borrow_rule(R, k):
    if k in R['B']:
        x = R['B'][k]
        return [tuple(e) for e in x['L']], tuple(x['a']), tuple(x['b'])
    p = R['Bpat']
    nmid = k - 1 - len(p['head']) - len(p['end'])
    if nmid < 0:
        raise EngError('borrow pattern undefined at k=%d' % k)
    L = [(p['m'], p['x0'] + p['x1'] * k)] + [(0, v) for v in p['head']] + [(0, p['mid'])] * nmid + \
        [(0, v) for v in p['end']]
    return L, tuple(p['a']), tuple(p['b'])


class Eng:
    def __init__(self, R, Q=20160, JMAX=400):
        self.R, self.Q, self.JMAX = R, Q, JMAX
        self.flags = []
        self.precond = []       # exact-phase rule applications outside the fitted range
        self.memo = {}          # (j, x) -> U_j(x) exact x
        self.tab = {}           # j -> np.array residues (U_j on huge inputs)
        self.const = {}         # j -> exact value if U_j is constant on huge inputs
        self.orbits = {}
        self.desc = {}
        self.Kc = {}            # j -> K_j (value fed to U_{j-1}^{l_1}) for borrow levels, constant part
        self.period = None      # (mu_L, P_L)
        self.lams = set()       # cycle lengths used by level tables
        self.calls = 0
        self.thr = self._thresholds()

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
            return Huge((m * x.r + c) % self.Q)
        return self.mk(m * x + c)

    def res(self, x):
        return x.r if isinstance(x, Huge) else x % self.Q

    def _thresholds(self):
        """smallest b from which the fitted borrow rule over k zeros holds (literal small scan); D/R2 exceptions"""
        thr = {}
        for k, lst in self.R.get('smallB', {}).items():
            bad = [b for b, *_ in lst]
            thr[int(k)] = (max(bad) + 1) if bad else 0
        # extrapolation for k beyond the fitted range: affine in k through the last two fitted thresholds
        ks = sorted(thr)
        self.thr_lin = None
        if len(ks) >= 2:
            k1, k2 = ks[-2], ks[-1]
            sl = (thr[k2] - thr[k1]) // max(1, k2 - k1)
            if sl < 0:
                sl = 0
            self.thr_lin = (sl, thr[k2] - sl * k2)
        return thr

    def threshold(self, k):
        if k in self.thr:
            return self.thr[k]
        if self.thr_lin is None:
            return 3 * k + 6
        # one unit of slack per extrapolated level (thresholds seen so far grow at most linearly)
        return max(0, self.thr_lin[0] * k + self.thr_lin[1] + (1 if self.thr_lin[0] else 0))

    # ----------------------------------------------------------------------------------------- level 0 (F0)
    def f0pow(self, n, x):
        """F0^n(x)"""
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
        # m >= 2
        if not isinstance(n, Huge) and not isinstance(x, Huge) and n * m.bit_length() < 60:
            v = x
            for _ in range(n):
                v = m * v + c
            return self.mk(v)
        if not isinstance(n, Huge):
            Mq = self.Q * (m - 1)
            T = (pow(m, n, Mq) * (self.res(x) * (m - 1) + c) - c) % Mq
            return Huge((T // (m - 1)) % self.Q)
        # huge n: orbit of the residue of x under F0 mod Q
        vals, mu, lam = self.orbit(0, x)
        return vals[self.index(n, mu, lam, len(vals))]

    # ----------------------------------------------------------------------------------------- one application
    def U(self, j, x):
        """U_j(x), j exact level index (may be > JMAX: mapped by periodicity)"""
        if j == 0:
            m, c = self.R['F0']
            return self.affv((m, c), x)
        j = self.rep(j)
        if isinstance(x, Huge):
            if j in self.const or j not in self.tab:
                self.table(j)
            if j in self.const:
                return self.const[j]
            return Huge(int(self.tab[j][x.r]))
        key = (j, x)
        if key in self.memo:
            return self.memo[key]
        self.calls += 1
        if self.calls > 2000000:
            raise EngError('evaluation budget')
        if j == 1:
            a = self.affv(self.R['A2'], x)
            b = self.affv(self.R['B2'], x)
            if self.R.get('excR2'):
                for bb, (ea, eb) in self.R['excR2']:
                    if bb == x:
                        a, b = ea, eb
            v = self.f0pow(a, b)
        else:
            k = j - 1
            th = self.threshold(k)
            if x < th:
                self.precond.append('B%d at exact b=%d (< fitted threshold %d)' % (k, x, th))
                lit = [e for e in self.R['smallB'].get(k, []) if e[0] == x]
                if lit and lit[0][1] == 'H':
                    raise EngError('HALT: borrow over %d zeros at b=%d halts' % (k, x))
                raise EngError('small-b borrow outside the fitted rule (k=%d b=%d: %s)' % (k, x, lit[:1]))
            L, fa, fb = borrow_rule(self.R, k)
            v = self.f0pow(self.affv(fa, x), self.affv(fb, x))
            for i in range(1, k + 1):          # position i holds L[k - i]
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

    def pow(self, j, n, x):
        """U_j^n(x)"""
        if n == 0:
            return x
        if j == 0:
            return self.f0pow(n, x)
        j = self.rep(j)
        d = self.level_desc(j)
        if d[0] == 'const':
            return d[1]
        if d[0] == 'add':                       # x -> x + C
            C = d[1]
            if (isinstance(n, Huge) and n.mod) or (isinstance(x, Huge) and x.mod):
                self.flags.append('reduced modulus in an additive level')
            if isinstance(n, Huge) or isinstance(x, Huge):
                return Huge((self.res(x) + C * self.res(n)) % self.Q)
            return self.mk(x + C * n)
        if not isinstance(n, Huge) and n <= 3:
            v = x
            for _ in range(n):
                v = self.U(j, v)
            return v
        vals, mu, lam = self.orbit(j, x)
        return vals[self.index(n, mu, lam, len(vals))]

    def orbit(self, j, x):
        key = (j, x)
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
            v = self.U(j, v) if j else self.affv(self.R['F0'], v)
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
                    raise EngError('slow exact orbit at level %d (additive level: counter?)' % j)
            vals.append(v)
        if mu is None:
            raise EngError('no cycle at level %d' % j)
        self.orbits[key] = (vals, mu, lam)
        return self.orbits[key]

    # ----------------------------------------------------------------------------------------- level structure
    def level_desc(self, j):
        """('const', v) | ('add', C) | ('gen',): structural shortcuts for U_j^n (level 1 only; others generic)"""
        if j in self.desc:
            return self.desc[j]
        R = self.R
        m1, c1 = R['F0']
        d = ('gen',)
        if j == 1 and not R.get('excR2'):
            mA, cA = R['A2']
            mB, cB = R['B2']
            if m1 == 0 and (mA > 0 or cA > 0):
                d = ('const', self.mk(c1))
            elif m1 == 1 and mA * c1 + mB == 1:
                d = ('add', cB + c1 * cA)
        self.desc[j] = d
        return d

    def rep(self, j):
        if j <= self.JMAX or self.period is None:
            if j > self.JMAX and self.period is None:
                self.find_period()
                if j > self.JMAX:
                    mu, P = self.period
                    return mu + (j - mu) % P
            return j
        mu, P = self.period
        return mu + (j - mu) % P

    def rep_huge(self, jr):
        """level index given as Huge residue (mod Q): requires P_L | Q"""
        if self.period is None:
            self.find_period()
        mu, P = self.period
        if self.Q % P:
            self.flags.append('level period %d does not divide Q' % P)
        return mu + (jr - mu) % P

    def table(self, j):
        """table of U_j on huge inputs"""
        if j in self.tab or j in self.const:
            return
        Q = self.Q
        R = self.R
        r = np.arange(Q, dtype=np.int64)
        if j == 1:
            mA, cA = R['A2']
            mB, cB = R['B2']
            m1, c1 = R['F0']
            if mA == 0 and mB == 0:
                self.const[1] = self.f0pow(self.mk(cA), self.mk(cB))
                return
            if m1 == 1:
                self.tab[1] = ((mB * r + cB + c1 * (mA * r + cA)) % Q).astype(np.int32)
                return
            if m1 == 0:
                self.const[1] = self.mk(c1)
                return
            if mB != 0:
                raise EngError('R2 with b-dependent b2 and multiplicative F0: unsupported')
            if mA == 0:
                self.const[1] = self.f0pow(self.mk(cA), self.mk(cB))
                return
            vals, mu, lam = self.orbit(0, self.mk(cB))
            if Q % lam:
                self.flags.append('L1 cycle %d does not divide Q' % lam)
            n = (mA * r + cA) % Q
            idx = mu + (n - mu) % lam
            arr = np.array([self.res(v) for v in vals], dtype=np.int64)
            self.tab[1] = arr[idx].astype(np.int32)
            return
        k = j - 1
        L, fa, fb = borrow_rule(R, k)
        if fa[0] != 0 or fb[0] != 0 or any(e[0] != 0 for e in L[1:]):
            raise EngError('borrow with b-dependent tail/a/b (k=%d): unsupported' % k)
        K = self.Kval(j)
        top = L[0]
        if top[0] == 0:
            self.const[j] = self.pow(k, self.mk(top[1]), K)
            return
        if top[0] < 0:
            raise EngError('negative refill slope')
        if k >= 1 and (k in self.const):
            self.const[j] = self.const[k]
            return
        n = (top[0] * r + top[1]) % Q
        d = self.level_desc(k) if k >= 1 else ('gen',)
        if d[0] == 'add':
            self.tab[j] = ((self.res(K) + d[1] * n) % Q).astype(np.int32)
            return
        vals, mu, lam = self.orbit(k, K)
        self.lams.add(lam)
        if Q % lam:
            self.flags.append('L%d cycle %d does not divide Q' % (j, lam))
        idx = mu + (n - mu) % lam
        arr = np.array([self.res(v) for v in vals], dtype=np.int64)
        self.tab[j] = arr[idx].astype(np.int32)

    def Kval(self, j):
        """K_j = clear(tail of L_{j-1}) (F0^{a}(b)) for constant tail/a/b"""
        if j in self.Kc:
            return self.Kc[j]
        k = j - 1
        L, fa, fb = borrow_rule(self.R, k)
        p = self.R['Bpat']
        v = None
        if k in self.R['B'] or k < p['k0'] + 3 or k - 1 - len(p['head']) <= len(p['end']):
            v = self.f0pow(self.mk(fa[1]), self.mk(fb[1]))
            for i in range(1, k):
                v = self.pow(i, self.mk(L[k - i][1]), v)
        else:
            # G recursion: G_k = value after clearing positions 1..k-1-|head|
            v = self.G(k)
            hl = len(p['head'])
            for idx in range(hl):            # head entries at positions k-1 .. k-hl; head[0] at position k-1
                pos = k - hl + idx
                v = self.pow(pos, self.mk(p['head'][hl - 1 - idx]), v)
        self.Kc[j] = v
        return v

    def G(self, k):
        """value after clearing positions 1..k-1-|head| of a borrow over k zeros (end + mid part)"""
        key = ('G', k)
        if key in self.Kc:
            return self.Kc[key]
        p = self.R['Bpat']
        hl, el = len(p['head']), len(p['end'])
        top = k - 1 - hl                  # highest mid position
        if top <= el + 1 or k <= p['k0'] + 2:
            L, fa, fb = borrow_rule(self.R, k)
            v = self.f0pow(self.mk(p['a'][1]), self.mk(p['b'][1]))
            for i in range(1, top + 1):
                v = self.pow(i, self.mk(L[k - i][1]), v)
        else:
            v = self.pow(top, self.mk(p['mid']), self.G(k - 1))
        self.Kc[key] = v
        return v

    def state_key(self, j):
        """state determining levels > j (for borrow levels in the pattern region)"""
        p = self.R['Bpat']
        hl = len(p['head'])
        parts = []
        for i in range(j - hl - 1, j + 1):
            self.table(i)
            parts.append(('c', self.res(self.const[i])) if i in self.const else ('t', self.tab[i].tobytes()))
        g = self.G(j)               # G for the borrow over j zeros (level j+1)
        import math
        M = 1
        for l in self.lams:
            M = M * l // math.gcd(M, l)
        return hash((tuple((a, b if a == 'c' else hash(b)) for a, b in parts), self.res(g), isinstance(g, Huge),
                     (p['x1'] * j) % M, M))

    def find_period(self):
        """exact recurrence of the level state"""
        seen = {}
        p = self.R['Bpat']
        j0 = max(p['k0'] + 4, max(self.R['B']) + 2, len(p['head']) + 3)
        for j in range(j0, self.JMAX + 1):
            try:
                key = self.state_key(j)
            except EngError as e:
                raise EngError('level state at %d: %s' % (j, e))
            if key in seen:
                mu = seen[key]
                P = j - mu
                # state_j == state_mu -> table_{j+1} == table_{mu+1} etc.: levels >= mu+1 periodic with period P
                self.period = (mu + 1, P)
                return
            seen[key] = j
        raise EngError('no level period up to %d' % self.JMAX)

    # ----------------------------------------------------------------------------------------- evaluation
    def value(self, ds, a, b):
        """exhaustion accumulator of K(ds; a; b), ds exact list"""
        v = self.f0pow(self.mk(a), self.mk(b))
        n = len(ds)
        for i in range(1, n + 1):
            v = self.pow(i, self.mk(ds[n - i]), v)
        return v

    def value_struct(self, pre, mid, cnt, suf, a, b):
        """exhaustion accumulator of K(pre + mid^cnt + suf; a; b), cnt exact int or (residue, modulus) for a huge count"""
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
            return v, None
        # huge count: running W over mid positions, eventually periodic in (level rep, W residue)
        if self.period is None:
            self.find_period()
        mu, P = self.period
        seen = {}
        Ws = []
        i = ns + 1
        W = v
        while True:
            jr = self.rep(i) if i > mu else i
            key = (jr if i > mu else ('x', i), self.res(W) if isinstance(W, Huge) else ('e', W))
            if i > mu and isinstance(W, Huge):
                if key in seen:
                    i0 = seen[key]
                    PW = i - i0
                    break
                seen[key] = i
            Ws.append((i, W))
            W = self.pow(i, self.mk(mid), W)
            i += 1
            if i > ns + 100000:
                raise EngError('no W period')
        # W after processing positions ns+1 .. ns+cnt: index cnt in Ws-list terms
        # Ws[t] = (position ns+1+t, W before applying position ns+1+t); W after cnt positions = Ws[cnt] (t = cnt)
        t0 = i0 - (ns + 1)
        cr, cmod = cnt
        if cmod % PW:
            self.flags.append('W period %d does not divide the count modulus %d' % (PW, cmod))
        t = t0 + (cr - t0) % PW
        Wc = Ws[t][1] if t < len(Ws) else None
        if Wc is None:
            raise EngError('W index')
        # top positions: level indices ns + cnt + i (huge): residue mod P
        mu, P = self.period
        if cmod % P:
            self.flags.append('level period %d does not divide the count modulus %d' % (P, cmod))
        v = Wc
        for i in range(1, len(pre) + 1):
            j = mu + ((ns + cr + i) - mu) % P
            v = self.pow(j, self.mk(pre[len(pre) - i]), v)
        return v, (t0, PW)


def eclass(R, E, V):
    """E = (p, cls) from fit_E; V exact or Huge -> (class c, rule, t)"""
    p, cls = E
    c = V.r % p if isinstance(V, Huge) else V % p
    return c, cls[c]
