"""rank7.py: record-level estimator for dlscan2 digit-list rows (CHAMPION / R4-SOME).

  python rank7.py IN.tsv [IN2.tsv ...] -o OUT.tsv [--grades CHAMPION,R4-SOME] [--steps 300000000] [--Q 20160]
                  [--only MACHINE] [--skip FILE] [--log LOG]

IN = dlscan2 output (machine, halted_step, n_templates, grade, template, params[, templates]); rows of the chosen
grades are ranked (duplicates across files are merged). OUT = ranked TSV, best first (see COLUMNS below);
a human-readable block per machine goes to --log (default OUT with .log).

Model (dlscan2's K(ds; a; b), ds = d1..dn, dn next to a; level j = digit d_(n+1-j), level 0 = a):
  F_0(b) = m1 b + c1                                 (R1: a -> a-1)
  F_1(b) = F_0^(m2 b + c2)(b2)                       (R2: dn -> dn-1, a := m2 b + c2, b := b2)
  F_j(b) = F_(j-1)^(x_j(b))(K_j), x_j = m3 b + c3 + e3 (j-1),
           K_j = F_(j-2)^t ... F_1^t F_0^a3 (b3)     (R3: borrow over k = j-1 zeros; tail t^(k-1), a := a3, b := b3)
  K(ds; a; b) runs to the exhaustion K(;0;b_E) (P empty: leading zeros vanish) or K(0^n;0;b_E) (P nonempty), with
  b_E = F_n^d1 ... F_1^dn F_0^a (b).  The exhaustion halts iff the literal probe pattern E(b) says so for b_E.
Numbers: exact while < 10^40, then 'huge' = (residue mod Q, level). Level l means N = 2^^^..(L arrows) h with
h in [3,4), l = L + (h-3) (written 2↑^L h). The BB(7) champion is l = 13 (2↑^13 3).
Arrow count u of a level: F_0 additive u=-1, multiplicative u=0; iterating a level with a count linear in b adds 1.
"""
import idle  # noqa: F401  (idle priority first)
import argparse
import math
import os
import random
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
RK7 = os.path.join(HERE, 'rk7.exe')
IDLE = 0x40
H = 10 ** 40
CHAMP_LEVEL = 13.0

COLUMNS = ['rank', 'machine', 'grade', 'verdict', 'est_level', 'beats_champ', 'halts', 'levels', 'base',
           'first_K', 'start_K', 'lockstep', 'rebuilds', 'runcheck', 'randcheck', 'exhaust', 'rules', 'template',
           'invariant', 'round2', 'refit', 'settled', 'notes']


# ------------------------------------------------------------------------------------------------ parsing
def parse_template(s):
    f = s.split(',')
    t = {'o': f[0], 'q': f[1]}
    for x in f[2:]:
        k, v = x.split('=', 1)
        t[k] = v
    al, be = t['d'].split('d+')
    alB, beB = t['b'].split('b+')
    return {'o': t['o'], 'q': t['q'], 'P': t['P'], 'u': t['u'], 's': t['s'], 'al': int(al), 'be': int(be),
            'alB': int(alB), 'beB': int(beB), 'S': t['S']}


def pinc_template(tmpl):
    """If the prefix P is a sequence of digits (u^(al d + be) s ...), return the P-inclusive template string (P = '-'),
    in which P's digits become the leading list digits (dlscan2's R4 probe K(;0;b) is then really a borrow from them;
    X33/Y19/Z16). Else None."""
    T = parse_template(tmpl)
    P = T['P']
    if P == '-':
        return None
    u, s = T['u'], T['s']
    i, digs = 0, []
    while i < len(P):
        v = 0
        while P.startswith(u, i):
            i += len(u)
            v += 1
        if not P.startswith(s, i):
            return None
        i += len(s)
        if v < T['be'] or (v - T['be']) % T['al']:
            return None
        digs.append((v - T['be']) // T['al'])
    if not digs or digs[0] == 0:
        return None
    f = tmpl.split(',')
    f = [('P=-' if x.startswith('P=') else x) for x in f]
    return ','.join(f)


def tmpl_args(T):
    return [T['o'], T['q'], T['P'], T['u'], T['s'], str(T['al']), str(T['be']), str(T['alB']), str(T['beB']), T['S']]


def lin(s):
    """'1b+3' / '3b-2' / '0b+0' -> (m, c)"""
    i = s.index('b')
    return int(s[:i]), int(s[i + 1:])


def parse_params(p):
    parts = [x.strip() for x in p.split('|')]
    R = {}
    R['m1'], R['c1'] = lin(parts[0].split()[1])
    r2 = parts[1].split()
    R['m2'], R['c2'] = lin(r2[1][2:])
    R['b2'] = int(r2[2][2:])
    r3 = parts[2].split()
    s = r3[1]                       # e.g. 3b+1+0k / 1b+3-1k
    i = s.index('b')
    R['m3'] = int(s[:i])
    rest = s[i + 1:-1]              # +1+0 / +3-1
    j = max(rest.rfind('+'), rest.rfind('-'))
    R['c3'], R['e3'] = int(rest[:j]), int(rest[j:])
    R['tail'] = int(r3[2].split('=')[1])
    R['a3'] = int(r3[3].split('=')[1])
    R['b3'] = int(r3[4].split('=')[1])
    R['r4'] = parts[3].split()[1]
    return R


# ------------------------------------------------------------------------------------------------ rk7 calls
def run_rk7(args, inp=None, timeout=None):
    p = subprocess.run([RK7] + args, input=inp, capture_output=True, text=True, creationflags=IDLE, timeout=timeout)
    return p.stdout


def trace(machine, T, steps, maxk):
    out = run_rk7(['trace', machine] + tmpl_args(T) + [str(steps), str(maxk)])
    ks, end = [], None
    for ln in out.splitlines():
        f = ln.split()
        if f[0] == 'K':
            ds = [] if f[2] == '-' else [int(x) for x in f[2].split(',')]
            ks.append((int(f[1]), ds, int(f[3]), int(f[4])))
        else:
            end = f
    return ks, end


def probe(machine, T, cfgs, N=2000000):
    """cfgs: list of (ds, a, b) -> list of ('K', ds, a, b, steps) / ('H', steps) / ('T',)"""
    if not cfgs:
        return []
    inp = ''.join('%s %d %d\n' % (','.join(map(str, ds)) if ds else '-', a, b) for ds, a, b in cfgs)
    out = run_rk7(['probe', machine] + tmpl_args(T) + [str(N)], inp)
    res = []
    for ln in out.splitlines():
        f = ln.split()
        if f[0] == 'K':
            res.append(('K', [] if f[1] == '-' else [int(x) for x in f[1].split(',')], int(f[2]), int(f[3]), int(f[4])))
        elif f[0] == 'H':
            res.append(('H', int(f[1])))
        else:
            res.append(('T',))
    while len(res) < len(cfgs):
        res.append(('T',))
    return res


# ------------------------------------------------------------------------------------------------ rule step
def fit_line(pts):
    """pts [(x, y)] -> (m, c) with y = m x + c for all points, or None"""
    if len(pts) < 2:
        return None
    (x0, y0), (x1, y1) = pts[0], pts[1]
    if x1 == x0 or (y1 - y0) % (x1 - x0):
        return None
    m = (y1 - y0) // (x1 - x0)
    c = y0 - m * x0
    return (m, c) if all(y == m * x + c for x, y in pts) else None


def refit_rules(machine, T, R0, Pempty, log):
    """Re-fit R1-R3 from targeted literal probes. dlscan2 stops collecting R3 points at the first tail digit other than
    0/1, so its 'tail' and 'e3' can be unfitted defaults (X33, Z16: real tails are 2s, refill -2k). Here:
      R1  K([2,1];a;b) -> K([2,1];a-1;m1 b+c1)            a = 1..3, b = 0..9
      R2  K([2,1];0;b) -> K([2,0];m2 b+c2;b2)             b = 0..9
      R3  K([1,2,0^k];0;b) -> K([1,1,x,t^(k-1)];a3;b3)    k = 1..4, b = 2k+2..2k+9; x = m3 b + c3 + e3 k
    Returns (R, report string, ok)."""
    R = dict(R0)
    rep = []
    ok = True
    pre = [] if Pempty else []
    cf = [(pre + [2, 1], a, b) for a in (1, 2, 3) for b in range(1, 10)]
    res = probe(machine, T, cf)
    pts = [(c[2], r[3]) for c, r in zip(cf, res) if r[0] == 'K' and r[1] == c[0] and r[2] == c[1] - 1]
    f = fit_line(pts) if len(pts) == len(cf) else None
    if f:
        R['m1'], R['c1'] = f
    else:
        ok = False
        rep.append('R1 refit failed (%d/%d)' % (len(pts), len(cf)))
    cf = [(pre + [2, 1], 0, b) for b in range(1, 10)]
    res = probe(machine, T, cf)
    good = [(c, r) for c, r in zip(cf, res) if r[0] == 'K' and norm(r[1], Pempty) == norm(pre + [2, 0], Pempty)]
    f = fit_line([(c[2], r[2]) for c, r in good]) if len(good) == len(cf) else None
    b2s = set(r[3] for c, r in good)
    if f and len(b2s) == 1:
        R['m2'], R['c2'], R['b2'] = f[0], f[1], b2s.pop()
    else:
        ok = False
        rep.append('R2 refit failed (%d/%d, b2 %s)' % (len(good), len(cf), sorted(b2s)))
    cf, keys = [], []
    for k in range(1, 5):
        for b in range(2 * k + 2, 2 * k + 10):
            cf.append(([1, 2] + [0] * k, 0, b))
            keys.append((k, b))
    res = probe(machine, T, cf)
    pts, tails, consts, bad = [], set(), set(), 0
    for (k, b), c, r in zip(keys, cf, res):
        if r[0] != 'K':
            bad += 1
            continue
        ds = r[1]
        if len(ds) != 2 + k or ds[0] != 1 or ds[1] != 1:
            bad += 1
            continue
        pts.append((k, b, ds[2]))
        tails.update(ds[3:])
        consts.add((r[2], r[3]))
    fitted = False
    if not bad and len(tails) <= 1 and len(consts) == 1:
        # x = m3 b + c3 + e3 k
        byk = {}
        for k, b, x in pts:
            byk.setdefault(k, []).append((b, x))
        lines = {k: fit_line(v) for k, v in byk.items()}
        if all(lines.values()) and len(set(l[0] for l in lines.values())) == 1:
            m3 = lines[1][0]
            ce = fit_line([(k, l[1]) for k, l in sorted(lines.items())])
            if ce:
                R['m3'], R['e3'], R['c3'] = m3, ce[0], ce[1]
                R['tail'] = tails.pop() if tails else R['tail']
                R['a3'], R['b3'] = consts.pop()
                fitted = True
    if not fitted:
        ok = False
        rep.append('R3 refit failed (bad %d, tails %s, consts %s)' % (bad, sorted(tails), sorted(consts)[:3]))
    diff = [k for k in ('m1', 'c1', 'm2', 'c2', 'b2', 'm3', 'c3', 'e3', 'tail', 'a3', 'b3') if R[k] != R0[k]]
    if diff:
        rep.append('refit differs from dlscan2 in ' + ','.join('%s:%s->%s' % (k, R0[k], R[k]) for k in diff))
    return R, '; '.join(rep) if rep else 'refit = dlscan2', ok


def rule_next(cfg, R, Pempty):
    """One dlscan2 macro step on an exact configuration. Returns ('K', ds, a, b, rule) or ('E', b)."""
    ds, a, b = cfg
    if a > 0:
        return ('K', list(ds), a - 1, R['m1'] * b + R['c1'], 'R1')
    if ds and ds[-1] > 0:
        nd = list(ds)
        nd[-1] -= 1
        r = ('K', nd, R['m2'] * b + R['c2'], R['b2'], 'R2')
    else:
        j = len(ds) - 1
        while j >= 0 and ds[j] == 0:
            j -= 1
        if j < 0:
            return ('E', b)
        k = len(ds) - 1 - j
        x = R['m3'] * b + R['c3'] + R['e3'] * k
        nd = list(ds[:j]) + [ds[j] - 1, x] + [R['tail']] * (k - 1)
        r = ('K', nd, R['a3'], R['b3'], 'R3')
    if Pempty:
        nd = r[1]
        while nd and nd[0] == 0:
            nd.pop(0)
    return r


def find_invariants(R, Pempty, mods=(2, 3, 4, 6), trials=400):
    """Linear forms Phi = ca a + cb b + cd sum(ds) mod m (not all coefficients 0, cb != 0) preserved by every rule
    step (rule_next) on random configurations. Returns [(m, ca, cb, cd)]."""
    rnd = random.Random(12345)
    cfgs = []
    for _ in range(trials):
        n = rnd.randint(1, 6)
        ds = [rnd.randint(0, 5) for _ in range(n)]
        if rnd.random() < 0.5:
            ds = ds[:max(1, n - 3)] + [0] * rnd.randint(1, 3)
            if not any(ds):
                ds[0] = 1
        a = 0 if rnd.random() < 0.5 else rnd.randint(1, 6)
        b = rnd.randint(10, 60)
        nx = rule_next((ds, a, b), R, Pempty)
        if nx[0] == 'K' and min(nx[1] + [nx[2], nx[3]]) >= 0:
            cfgs.append(((ds, a, b), (nx[1], nx[2], nx[3])))
    out = []
    for m in mods:
        for ca in range(m):
            for cb in range(1, m):
                for cd in range(m):
                    if all((ca * a + cb * b + cd * sum(ds) - ca * a2 - cb * b2 - cd * sum(d2)) % m == 0
                           for (ds, a, b), (d2, a2, b2) in cfgs):
                        out.append((m, ca, cb, cd))
    # keep the smallest modulus representatives (drop multiples of a smaller found form)
    return out


def phi(inv, cfg):
    m, ca, cb, cd = inv
    ds, a, b = cfg
    return (ca * a + cb * b + cd * sum(ds)) % m


def invariant_check(machine, T, R, Pempty, start, n, patL, presL, B0):
    """Does a rule invariant exclude every halting exhaustion? Uses the large-b exhaustion window (b = B0..B0+23):
    an exhaustion K(;0;b) / K(0^n;0;b) has Phi = cb b. Returns (verdict string or None, detail)."""
    invs = find_invariants(R, Pempty)
    if not invs:
        return None, 'no linear invariant mod 2,3,4,6'
    det = []
    for inv in invs:
        m, ca, cb, cd = inv
        p0 = phi(inv, (start[1], start[2], start[3]))
        allowed = [(B0 + i, r) for i, r in enumerate(presL) if (cb * (B0 + i)) % m == p0]
        if not allowed:
            continue
        kinds = set(r[0] for _, r in allowed)
        if 'H' in kinds:
            det.append('Phi=%da+%db+%dsum mod %d = %d allows a halting exhaustion' % (ca, cb, cd, m, p0))
            continue
        if kinds != {'K'}:
            det.append('Phi mod %d: allowed exhaustions leave the template (%s)' % (m, ''.join(sorted(kinds))))
            continue
        # every allowed exhaustion rebuilds: does the rebuild keep Phi?
        keep = all(phi(inv, (r[1], r[2], r[3])) == p0 for _, r in allowed)
        s = 'Phi=%da+%db+%dsum(ds) mod %d = %d at the run; halting exhaustions excluded%s' % (
            ca, cb, cd, m, p0, '; rebuild keeps Phi -> NEVER HALTS' if keep else ' at the next exhaustion only')
        return ('NEVER-HALTS(invariant)' if keep else 'NO-HALT-NEXT(invariant)'), s
    return None, '; '.join(det[:3]) if det else 'invariants found but none decisive'


def norm(ds, Pempty):
    ds = list(ds)
    if Pempty:
        while ds and ds[0] == 0:
            ds.pop(0)
    return ds


def same(r, p, Pempty):
    return r[0] == 'K' and norm(r[1], Pempty) == norm(p[1], Pempty) and r[2] == p[2] and r[3] == p[3]


# ------------------------------------------------------------------------------------------------ numbers
def lvl_int(n):
    """level of an exact nonnegative integer (2↑^L h, h in [3,4) -> L + h - 3); numbers below 8 get n/8"""
    if n < 8:
        return n / 8.0
    if n < 16:
        return 1 + (n - 8) / 8.0
    if n < 65536:
        return 2 + (math.log2(n) - 4) / 12.0
    lg = n.bit_length()
    return 3 + min(0.99, (math.log2(lg) - 4) / 65532.0 * 4000)   # 2↑^3 3 = 65536 .. 2↑^4 3 = 2↑↑65536


def arrow_apply(u, l):
    """level of 2↑^u N for N of level l (u >= 1).  N below 2↑^u 4 = 2↑^(u+1) 3: 2↑^u N = 2↑^(u+1)(1 + slog N), level
    u+1 .. u+2 (interpolated linearly in l); N = 2↑^(u+1) h: 2↑^(u+1)(h+1), just above 2↑^(u+2) 3;
    N far above: unchanged."""
    if l < u + 1:
        return u + 1 + max(0.0, l) / (u + 1)
    if l < u + 2:
        return u + 2 + 0.1 * (l - u - 1)
    return l + 0.001


class Num:
    __slots__ = ('ex', 'r', 'lv')

    def __init__(self, ex=None, r=0, lv=0.0):
        self.ex, self.r, self.lv = ex, r, lv

    def huge(self):
        return self.ex is None

    def key(self):
        return ('e', self.ex) if self.ex is not None else ('h', self.r)

    def __repr__(self):
        return str(self.ex) if self.ex is not None else 'H(l=%.2f,r=%d)' % (self.lv, self.r)


class Model:
    """Rule-level evaluator: exact / (residue mod Q, level) arithmetic."""

    def __init__(self, R, Q):
        self.R, self.Q = R, Q
        self.desc = {}        # level -> ('const', Num) / ('id',) / ('lin', 1, C Num) / ('gen',)
        self.u = {}           # level -> arrow count (None = constant)
        self.Kc = {}          # level -> K_j Num
        self.memo = {}
        self.orbits = {}
        self.flags = []
        self.precond = []
        self.calls = 0

    def mk(self, n):
        if n < 0:
            self.precond.append('negative value %d' % n)
            n = 0
        if n < H:
            return Num(n, n % self.Q, lvl_int(n))
        return Num(None, n % self.Q, lvl_int(n) if n.bit_length() < 10 ** 6 else 3.5)

    def aff(self, m, x, c):
        """m*x + c"""
        if x.ex is not None:
            return self.mk(m * x.ex + c)
        if m == 0:
            return self.mk(c)
        return Num(None, (m * x.r + c) % self.Q, x.lv)

    def add(self, x, y):
        if x.ex is not None and y.ex is not None:
            return self.mk(x.ex + y.ex)
        return Num(None, (x.r + y.r) % self.Q, max(x.lv, y.lv))

    def mul(self, x, y):
        if x.ex is not None and y.ex is not None:
            return self.mk(x.ex * y.ex)
        if (x.ex == 0) or (y.ex == 0):
            return self.mk(0)
        return Num(None, (x.r * y.r) % self.Q, max(x.lv, y.lv))

    # level descriptors
    def level(self, j):
        if j in self.desc:
            return self.desc[j]
        R = self.R
        if j == 0:
            m, c = R['m1'], R['c1']
            if m == 0:
                d, u = ('const', self.mk(c)), None
            elif m == 1:
                d, u = (('lin', 1, self.mk(c)), -1) if c else (('id',), None)
            else:
                d, u = ('gen',), 0
            self.desc[0], self.u[0] = d, u
            return d
        prev = self.level(j - 1)
        up = self.u[j - 1]
        m = R['m2'] if j == 1 else R['m3']
        c = R['c2'] if j == 1 else R['c3'] + R['e3'] * (j - 1)
        K = self.K(j)
        if prev[0] == 'id':
            d, u = ('const', K), None
        elif prev[0] == 'const':
            d, u = ('const', prev[1]), None
        elif m == 0:
            v = self.apply(j - 1, self.mk(max(c, 0)), K)
            d, u = ('const', v), None
        elif prev[0] == 'lin':
            C = prev[2]
            # F_j(b) = K + C (m b + c)
            if C.ex is not None and C.ex * m == 1:
                if K.ex is not None:
                    const = self.mk(K.ex + C.ex * c)
                else:
                    const = Num(None, (K.r + C.ex * c) % self.Q, K.lv)
                d, u = ('lin', 1, const), -1
            else:
                d, u = ('gen',), 0
        else:
            d, u = ('gen',), up + 1
        self.desc[j], self.u[j] = d, u
        return d

    def K(self, j):
        if j in self.Kc:
            return self.Kc[j]
        R = self.R
        if j == 1:
            v = self.mk(R['b2'])
        else:
            v = self.apply(0, self.mk(R['a3']), self.mk(R['b3']))
            for i in range(1, j - 1):
                v = self.apply(i, self.mk(R['tail']), v)
        self.Kc[j] = v
        return v

    def x(self, j, b):
        R = self.R
        if j == 1:
            return self.aff(R['m2'], b, R['c2'])
        c = R['c3'] + R['e3'] * (j - 1)
        if b.ex is not None:
            v = R['m3'] * b.ex + c
            if v < 1:
                self.precond.append('refill x_%d(b=%d) = %d < 1' % (j, b.ex, v))
            return self.mk(max(v, 0))
        return self.aff(R['m3'], b, c)

    def levelF(self, j, l):
        """level of F_j(b) for b of level l"""
        u = self.u.get(j)
        if u is None or u <= 0:
            return l
        return arrow_apply(u, l)

    def F(self, j, b):
        """one application of level j"""
        key = (j, b.key())
        if key in self.memo:
            v = self.memo[key]
            if v.huge() and b.huge():
                v = Num(None, v.r, self.levelF(j, b.lv))
            return v
        self.calls += 1
        if self.calls > 3000000:
            raise RuntimeError('evaluation budget')
        if j == 0:
            R = self.R
            v = self.aff(R['m1'], b, R['c1'])
        else:
            xb = self.x(j, b)
            v = self.apply(j - 1, xb, self.K(j))
        if v.huge() and b.huge():
            v = Num(None, v.r, self.levelF(j, b.lv))
        self.memo[key] = v
        return v

    def lvl_iter(self, j, d, b, first):
        """level estimate of F_j^d(b) for a huge result; first = level after a few applications"""
        u = self.u.get(j)
        if u is None:
            return max(first, b.lv)
        if u <= -1:
            return max(first, b.lv, d.lv)
        return max(first, arrow_apply(u + 1, d.lv) if d.lv >= 1 else first)

    def apply(self, j, d, b):
        """F_j^d(b)"""
        desc = self.level(j)
        if d.ex == 0 or desc[0] == 'id':
            return b
        if desc[0] == 'const':
            return desc[1]
        if desc[0] == 'lin':
            return self.add(b, self.mul(desc[2], d))
        # general: loop a few times, else orbit
        if d.ex is not None and d.ex <= 8:
            v = b
            for _ in range(d.ex):
                v = self.F(j, v)
            return v
        vals, mu, lam = self.orbit(j, b)
        if d.ex is not None:
            if d.ex < len(vals):
                return vals[d.ex]
            idx = mu + (d.ex - mu) % lam
        else:
            if self.Q % lam:
                self.flags.append('cycle %d of level %d does not divide Q' % (lam, j))
            idx = mu + (d.r - mu) % lam
        res = vals[idx]
        if b.huge():
            first = b.lv
            for _ in range(4):
                first = self.levelF(j, first)
        else:
            first = vals[min(len(vals) - 1, 4)].lv
        return Num(None, res.r, self.lvl_iter(j, d, b, first))

    def orbit(self, j, b):
        key = (j, b.key())
        if key in self.orbits:
            return self.orbits[key]
        vals = [b]
        seen = {}
        v = b
        if v.huge():
            seen[v.r] = 0
        mu = lam = None
        for i in range(1, 4 * self.Q + 400):
            v = self.F(j, v)
            if v.huge():
                if v.r in seen:
                    mu, lam = seen[v.r], i - seen[v.r]
                    break
                seen[v.r] = i
            vals.append(v)
        if mu is None:
            raise RuntimeError('no cycle at level %d' % j)
        self.orbits[key] = (vals, mu, lam)
        return self.orbits[key]

    def run(self, ds, a, b):
        """exhaustion accumulator from K(ds; a; b)"""
        v = self.apply(0, self.mk(a), self.mk(b))
        n = len(ds)
        for j in range(1, n + 1):
            v = self.apply(j, self.mk(ds[n - j]), v)
        return v


# ------------------------------------------------------------------------------------------------ analysis
def period_of(s):
    for p in range(1, 13):
        if all(s[i] == s[i + p] for i in range(len(s) - p)):
            return p
    return None


def halting_pattern(machine, T, n_zero, Pempty, bmax=47):
    """Exhaustion probes E(b) = K(0^n;0;b) (P nonempty) or K(;0;b): a small window b = 0..bmax and a large window
    b = B0..B0+23 with B0 = max(bmax+1, 4n+40) (thresholds like 'halts iff b < 2n' only show at b >> n).
    Returns (small pattern, large pattern, B0, period of the large window, small results, large results)."""
    ds = [] if Pempty else [0] * n_zero
    B0 = max(bmax + 1, 4 * n_zero + 40)
    res = probe(machine, T, [(ds, 0, b) for b in range(bmax + 1)], N=3000000)
    resL = probe(machine, T, [(ds, 0, b) for b in range(B0, B0 + 24)], N=20000000)
    pat = ''.join(r[0] for r in res)
    patL = ''.join(r[0] for r in resL)
    return pat, patL, B0, period_of(patL), res, resL


def follow(machine, T, cfg, N=3000000, maxp=3):
    ds, a, b = cfg
    inp = '%s %d %d\n' % (','.join(map(str, ds)) if ds else '-', a, b)
    return run_rk7(['follow', machine] + tmpl_args(T) + [str(N), str(maxp)], inp).strip().splitlines()


def analyse(machine, grade, tmpl, params, args, log):
    T = parse_template(tmpl)
    R = parse_params(params)
    Pempty = T['P'] == '-'
    row = {'machine': machine, 'grade': grade, 'template': tmpl,
           'rules': 'R1 %db%+d | R2 a=%db%+d b=%d | R3 %db%+d%+dk t=%d a=%d b=%d | R4 %s' % (
               R['m1'], R['c1'], R['m2'], R['c2'], R['b2'], R['m3'], R['c3'], R['e3'], R['tail'], R['a3'], R['b3'], R['r4'])}
    notes = []
    L = ['=' * 100, '%s  %s  %s' % (machine, grade, tmpl), '  rules (dlscan2): ' + row['rules']]
    R, rep, fit_ok = refit_rules(machine, T, R, Pempty, log)
    row['refit'] = rep
    row['rules'] = 'R1 %db%+d | R2 a=%db%+d b=%d | R3 %db%+d%+dk t=%d a=%d b=%d' % (
        R['m1'], R['c1'], R['m2'], R['c2'], R['b2'], R['m3'], R['c3'], R['e3'], R['tail'], R['a3'], R['b3'])
    L.append('  rules (refit):   %s   [%s]' % (row['rules'], rep))
    if not fit_ok:
        notes.append('refit incomplete: ' + rep)
    # (a) literal trace from the blank tape
    ks, end = trace(machine, T, args.steps, args.maxk)
    row['first_K'] = '-' if not ks else 'step %d n=%d ds=[%s] a=%d b=%d' % (
        ks[0][0], len(ks[0][1]), ','.join(map(str, ks[0][1])), ks[0][2], ks[0][3])
    L.append('  literal: %d K-configs, end %s; first %s' % (len(ks), ' '.join(end or ['?']), row['first_K']))
    lit_halt = bool(end) and end[0] == 'HALT'
    # (b1) lockstep on the literal trace
    bad, rebuilds = [], []
    for i in range(len(ks) - 1):
        nx = rule_next(tuple(ks[i][1:]), R, Pempty)
        if nx[0] == 'E':
            rebuilds.append((ks[i + 1][0], nx[1], len(ks[i + 1][1])))    # (step, b at exhaustion, new list length)
        elif not same(nx, ('K',) + tuple(ks[i + 1][1:]), Pempty):
            bad.append(i)
    row['rebuilds'] = '-' if not rebuilds else '%d: ' % len(rebuilds) + ' '.join(
        'b=%d->n=%d' % (r[1], r[2]) for r in rebuilds[:6])
    if rebuilds:
        L.append('  literal exhaustions that REBUILT (step, b, new n): %s' % rebuilds[:10])
    row['lockstep'] = '%d/%d' % (len(ks) - 1 - len(bad) - len(rebuilds), max(0, len(ks) - 1 - len(rebuilds)))
    if bad:
        i = bad[-1]
        L.append('  lockstep: %d mismatches; last at K#%d step %d: %s -> literal %s, rules %s' % (
            len(bad), i, ks[i][0], ks[i][1:], ks[i + 1][1:], rule_next(tuple(ks[i][1:]), R, Pempty)[:4]))
        row['lockstep'] += ' miss (last K#%d)' % i
    if lit_halt:
        L.append('  literal run HALTS at step %s with %s ones' % (end[1], end[2]))
        notes.append('literal halt step %s ones %s' % (end[1], end[2]))
    # start configuration for the rule-level run: the last literal K-config (rules checked on all pairs after the
    # last mismatch)
    start = ks[-1] if ks else None
    row['start_K'] = '-' if start is None else 'step %d n=%d ds=[%s] a=%d b=%d' % (
        start[0], len(start[1]), ','.join(map(str, start[1][:30])) + (',..' if len(start[1]) > 30 else ''), start[2], start[3])
    # (b2) rule-level continuation from start, each config probed literally (while small)
    runcheck = '-'
    if start is not None and not lit_halt:
        cfgs, preds, cur, exh = [], [], (list(start[1]), start[2], start[3]), None
        for _ in range(args.runcheck):
            nx = rule_next(cur, R, Pempty)
            if nx[0] == 'E':
                exh = nx[1]
                break
            if max([cur[1], cur[2]] + cur[0]) > args.probe_max:
                break
            cfgs.append(cur)
            preds.append(nx)
            cur = (nx[1], nx[2], nx[3])
        res = probe(machine, T, cfgs, N=args.probeN)
        ok = nt = 0
        firstbad = None
        for c, p, r in zip(cfgs, preds, res):
            if same(r, p, Pempty):
                ok += 1
            elif r[0] == 'T':
                nt += 1
            elif firstbad is None:
                firstbad = (c, p[:4], r)
        runcheck = '%d/%d' % (ok, len(cfgs)) + (' T=%d' % nt if nt else '')
        if firstbad:
            L.append('  runcheck first miss: %s rules->%s literal->%s' % firstbad)
            runcheck += ' miss'
        if exh is not None:
            runcheck += ' (reached exhaustion b=%d)' % exh
    row['runcheck'] = runcheck
    # (b3) random small configurations
    rnd = random.Random(sum(map(ord, machine)))
    rc, rp = [], []
    for _ in range(args.rand):
        n = rnd.randint(1, 5)
        ds = [rnd.randint(0, 4) for _ in range(n)]
        if Pempty and ds[0] == 0:
            ds[0] = rnd.randint(1, 4)
        a, b = rnd.randint(0, 6), rnd.randint(0, 8)
        if rnd.random() < 0.6:                      # force borrows over k >= 1 zeros (dlscan2's fit barely sees k >= 2)
            k = rnd.randint(1, 4)
            ds = [rnd.randint(1, 4)] + [rnd.randint(0, 4) for _ in range(rnd.randint(0, 2))] + [rnd.randint(1, 4)] + [0] * k
            a, b = 0, rnd.randint(2 * k + 2, 2 * k + 12)
        nx = rule_next((ds, a, b), R, Pempty)
        if nx[0] != 'K' or min(nx[1] + [nx[2], nx[3]]) < 0:
            continue
        rc.append((ds, a, b))
        rp.append(nx)
    res = probe(machine, T, rc, N=args.probeN)
    ok, miss, nt = 0, [], 0
    for c, p, r in zip(rc, rp, res):
        if same(r, p, Pempty):
            ok += 1
        elif r[0] == 'T':
            nt += 1
        else:
            miss.append((c, p[4], r))
    row['randcheck'] = '%d/%d' % (ok, len(rc)) + (' T=%d' % nt if nt else '')
    if miss:
        byrule = {}
        for c, rule, r in miss:
            byrule.setdefault(rule, []).append((c, r[:4]))
        L.append('  randcheck misses by rule: ' + '; '.join('%s x%d e.g. %s -> %s' % (k, len(v), v[0][0], v[0][1])
                                                            for k, v in byrule.items()))
        row['randcheck'] += ' miss ' + ','.join('%s:%d' % (k, len(v)) for k, v in byrule.items())
    # (c) level structure and evaluation
    M = Model(R, args.Q)
    est, halts, exh_s, levels_s, base_s = None, '?', '-', '-', '-'
    if start is not None and not lit_halt:
        n = len(start[1])
        try:
            for j in range(0, n + 1):
                M.level(j)
            us = [M.u[j] for j in range(n + 1)]
            levels_s = 'u=' + ','.join('c' if x is None else str(x) for x in us)
            nm = {None: 'const', -1: 'add', 0: 'mult'}
            base_s = nm.get(us[0], str(us[0])) + '/F1:' + (nm.get(us[1], str(us[1])) if n >= 1 else '-')
            bE = M.run(start[1], start[2], start[3])
            est = bE.lv
            pat, patL, B0, per, pres, presL = halting_pattern(machine, T, n, Pempty)
            hb = None                       # a b-value in the probed windows with the same behaviour as b_E
            if bE.ex is not None and bE.ex < len(pat):
                h = pat[bE.ex]
                hb = bE.ex
                exh_s = 'b_E=%d' % bE.ex
            elif bE.ex is not None and bE.ex < B0:
                r1 = probe(machine, T, [([] if Pempty else [0] * n, 0, bE.ex)], N=20000000)[0]
                h = r1[0]
                hb = bE.ex
                exh_s = 'b_E=%d' % bE.ex
            else:
                h = '?'
                bres = bE.ex % args.Q if bE.ex is not None else bE.r
                if per is not None and args.Q % per == 0:
                    for i in range(B0, B0 + per):
                        if i % per == bres % per:
                            h, hb = patL[i - B0], i
                elif per is not None:
                    notes.append('pattern period %d does not divide Q' % per)
                exh_s = ('b_E=%d' % bE.ex) if bE.ex is not None else 'b_E~l%.2f r%%%d=%d' % (bE.lv, args.Q, bE.r)
            exh_s += ' E(b0..47)=%s E(b%d..)=%s per=%s' % (pat, B0, patL, per)
            halts = {'H': 'yes', 'K': 'no(rebuild)', 'T': 'no?(leaves template)'}.get(h, '?')
            if fit_ok:
                iv, idet = invariant_check(machine, T, R, Pempty, start, n, patL, presL, B0)
                row['invariant'] = idet
                L.append('  invariant search: ' + idet)
                if iv:
                    notes.append(iv)
                    row['inv_verdict'] = iv
            else:
                row['invariant'] = 'skipped (refit failed)'
            if h == 'K' and Pempty and per:
                # round-2 sweep: evaluate the exhaustion reached from each rebuilt list of the large window; class
                # transitions c = b mod per -> c' = b_E2 mod per show whether a halting class is ever reachable
                M2 = Model(R, args.Q2 if args.Q2 % per == 0 else args.Q)
                trans = {}
                for i, rr in enumerate(presL):
                    if rr[0] != 'K':
                        continue
                    try:
                        v = M2.run(rr[1], rr[2], rr[3])
                    except (RuntimeError, RecursionError):
                        continue
                    c2 = (v.ex if v.ex is not None else v.r) % per
                    trans.setdefault((B0 + i) % per, set()).add(c2)
                c0 = (bE.ex if bE.ex is not None else bE.r) % per
                seen, todo, halt_reach, mixed = set(), [c0], False, False
                while todo:
                    c = todo.pop()
                    if c in seen:
                        continue
                    seen.add(c)
                    nxt = trans.get(c)
                    if not nxt:
                        mixed = True
                        continue
                    if len(nxt) > 1:
                        mixed = True
                    for c2 in nxt:
                        hh = patL[(c2 - B0) % per] if per else '?'
                        if hh == 'H':
                            halt_reach = True
                        elif hh == 'K':
                            todo.append(c2)
                tr_s = ' '.join('%d->%s' % (c, ','.join(map(str, sorted(v)))) for c, v in sorted(trans.items()))
                row['round2'] = 'classes mod %d: %s; from %d: %s' % (
                    per, tr_s, c0, 'HALT REACHABLE' if halt_reach else ('unclear' if mixed else 'never halts (rebuild forever)'))
                if not fit_ok:
                    row['round2'] = 'UNRELIABLE (rule refit failed; A1/A2/B1 were called never-halting this way and halt): ' + row['round2']
                L.append('  round-2 sweep: ' + row['round2'])
                if not fit_ok:
                    notes.append('round-2 not trusted: rules not refit')
                elif halt_reach:
                    notes.append('round-2: a halting exhaustion class is reachable -> f_(w+1)-class candidate, check!')
                elif not mixed:
                    notes.append('round-2: no halting class reachable (parity-type invariant)')
            if h == 'K':
                rr = presL[hb - B0] if hb is not None and hb >= B0 else pres[hb] if hb is not None else None
                if rr is not None:
                    L.append('  exhaustion at b=%d rebuilds in template: n=%d %s' % (hb, len(rr[1]), rr[:4]))
                    notes.append('E(b=%d) rebuilds a %d-digit list' % (hb, len(rr[1])))
            if h == 'T' and hb is not None:
                fl = follow(machine, T, ([] if Pempty else [0] * n, 0, hb))
                L.append('  exhaustion at b=%d leaves the template; literal follow: %s' % (hb, ' | '.join(x[:160] for x in fl)))
                notes.append('E(b=%d) leaves template (hidden digit in P / off-template rebuild): follow up' % hb)
            if M.flags:
                notes.append('mod-Q uncertain: ' + M.flags[0])
            if M.precond:
                notes.append('precondition: ' + M.precond[0] + (' (+%d)' % (len(M.precond) - 1) if len(M.precond) > 1 else ''))
        except (RuntimeError, RecursionError) as e:
            notes.append('evaluation failed: %s' % e)
    row['levels'], row['base'], row['exhaust'], row['halts'] = levels_s, base_s, exh_s, halts
    row['est_level'] = '-' if est is None else '%.2f' % est
    beats = '-'
    if est is not None:
        beats = 'YES' if est > CHAMP_LEVEL + 0.5 else ('CLOSE' if est >= CHAMP_LEVEL - 1.5 else 'no')
    row['beats_champ'] = beats
    if lit_halt:
        v = 'SMALL-HALT'
    elif start is None:
        v = 'NO-K'
    elif est is None:
        v = 'UNEVALUATED'
    elif row.get('inv_verdict') and halts == 'yes':
        v = 'CONFLICT(invariant vs residue)'
    elif row.get('inv_verdict', '').startswith('NEVER-HALTS'):
        v = 'NEVER-HALTS(invariant)'
    elif halts.startswith('no(rebuild'):
        v = 'REBUILD'
    elif halts.startswith('no?'):
        v = 'LEAVES-TEMPLATE'
    elif halts == '?':
        v = 'HALT-UNKNOWN'
    else:
        v = {'YES': 'RECORD?', 'CLOSE': 'CLOSE', 'no': 'below'}[beats]
    if 'miss' in row['lockstep'] or 'miss' in row['randcheck'] or 'miss' in row['runcheck']:
        v += '+RULE-MISS'
    if not fit_ok:
        v += '+RULES?'
    row['verdict'] = v
    row['notes'] = '; '.join(notes) if notes else '-'
    L.append('  start %s | levels %s base %s' % (row['start_K'], levels_s, base_s))
    L.append('  checks: lockstep %s runcheck %s randcheck %s' % (row['lockstep'], row['runcheck'], row['randcheck']))
    L.append('  exhaustion %s halts %s | est level %s (champion %.1f) -> %s' % (exh_s, halts, row['est_level'], CHAMP_LEVEL, v))
    if notes:
        L.append('  notes: ' + row['notes'])
    log.write('\n'.join(L) + '\n')
    log.flush()
    return row


def read_rows(inputs, grades, only=None):
    rows, seen = [], set()
    for fn in inputs:
        for ln in open(fn, encoding='utf-8', errors='replace'):
            f = ln.rstrip('\n').split('\t')
            if len(f) < 6 or f[3] not in grades or f[0] in seen:
                continue
            if only and f[0] != only:
                continue
            seen.add(f[0])
            rows.append((f[0], f[3], f[4], f[5]))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('inputs', nargs='+')
    ap.add_argument('-o', '--out', required=True)
    ap.add_argument('--grades', default='CHAMPION,R4-SOME')
    ap.add_argument('--steps', type=int, default=300000000)
    ap.add_argument('--maxk', type=int, default=3000)
    ap.add_argument('--Q', type=int, default=2 ** 6 * 9 * 5 * 7)
    ap.add_argument('--Q2', type=int, default=720, help='modulus for the round-2 sweep')
    ap.add_argument('--runcheck', type=int, default=300)
    ap.add_argument('--probe_max', type=int, default=3000)
    ap.add_argument('--probeN', type=int, default=3000000)
    ap.add_argument('--rand', type=int, default=60)
    ap.add_argument('--only', default=None)
    ap.add_argument('--settled', default=None,
                    help='file "machine label..." of machines settled elsewhere (still ranked, label shown)')
    ap.add_argument('--log', default=None)
    args = ap.parse_args()
    skip = {}
    if args.settled:
        for ln in open(args.settled, encoding='utf-8'):
            if ln.strip() and not ln.startswith('#'):
                f = ln.split(None, 1)
                skip[f[0]] = f[1].strip() if len(f) > 1 else 'settled'
    rows = read_rows(args.inputs, set(args.grades.split(',')), args.only)
    logfn = args.log or os.path.splitext(args.out)[0] + '.log'
    out = []
    with open(logfn, 'w', encoding='utf-8') as log:
        for i, (m, g, t, p) in enumerate(rows):
            t0 = time.time()
            try:
                row = analyse(m, g, t, p, args, log)
                tp = pinc_template(t)
                if tp and row.get('verdict', '').split('+')[0] in ('LEAVES-TEMPLATE', 'REBUILD', 'HALT-UNKNOWN', 'NO-K'):
                    log.write('  -> P-inclusive re-analysis with template %s\n' % tp)
                    row2 = analyse(m, g, tp, p, args, log)
                    row2['notes'] = 'P-inclusive (orig %s: %s, level %s); %s' % (
                        t, row.get('verdict'), row.get('est_level'), row2.get('notes', '-'))
                    row = row2
            except Exception as e:  # keep going
                row = {'machine': m, 'grade': g, 'template': t, 'verdict': 'ERROR', 'est_level': '-', 'notes': repr(e)}
                log.write('%s ERROR %r\n' % (m, e))
            row['settled'] = skip.get(m, '-')
            out.append(row)
            print('%d/%d %s %s level %s %s (%.0fs)' % (i + 1, len(rows), m, g, row.get('est_level'), row.get('verdict'),
                                                       time.time() - t0), flush=True)

    def key(r):
        v = r.get('verdict', '')
        try:
            e = float(r.get('est_level', '-'))
        except ValueError:
            e = -1
        cls = {'RECORD?': 0, 'CLOSE': 0, 'CONFLICT(invariant vs residue)': 0, 'HALT-UNKNOWN': 1, 'NEVER-HALTS(invariant)': 3, 'LEAVES-TEMPLATE': 1, 'REBUILD': 2, 'below': 3}.get(
            v.split('+')[0], 4)
        return (r.get('settled', '-') != '-', cls, -e)
    out.sort(key=key)
    with open(args.out, 'w', newline='\n', encoding='utf-8') as f:
        f.write('\t'.join(COLUMNS) + '\n')
        for i, r in enumerate(out):
            r['rank'] = str(i + 1)
            f.write('\t'.join(str(r.get(c, '-')) for c in COLUMNS) + '\n')


if __name__ == '__main__':
    sys.setrecursionlimit(20000)
    main()
