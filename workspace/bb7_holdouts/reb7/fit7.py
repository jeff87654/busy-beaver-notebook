"""fit7.py: generic K-level rule fitter for digit-list machines (reb7), on top of rk7.exe's literal prober.

Configuration K(ds; a; b) in a dlscan template (rk7 semantics: next parseable K-moment). ds top-first, ds[-1] next to a.
Rules fitted from literal probes (nothing taken from dlscan2's params):
  D   K(X; a+1; b)            -> K(X; a; F0(b))                       F0 affine
  R2  K(X,d+1; 0; b)          -> K(X,d; A2(b); B2(b))                 affine
  Bk  K(X,y+1,0^k; 0; b)      -> K(X,y,L_k(b); a_k(b); b_k(b))        L_k = k entries, each affine in b (k = 1..KF)
      extrapolated for k > KF: L_k = [x0 + x1 k + m b] + head + mid^(k-1-|head|-|end|) + end, a_k, b_k constant
  E   K(;0;b) (P empty) or K(0^n;0;b) (P nonempty): per class of b mod pE: HALT / rebuild (list = pre + mid^cnt + suf,
      cnt affine in b within the class) / other.
Small-b behaviour of every rule (thresholds, halts) is recorded in 'small'.
"""
import idle  # noqa: F401
import subprocess
import random

RK7 = r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\rank\rk7.exe'
IDLE = 0x40


# --------------------------------------------------------------------------------------------- template
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


def tstr(T):
    return '%s,%s,P=%s,u=%s,s=%s,d=%dd+%d,b=%db+%d,S=%s' % (T['o'], T['q'], T['P'], T['u'], T['s'], T['al'], T['be'],
                                                           T['alB'], T['beB'], T['S'])


def targs(T):
    return [T['o'], T['q'], T['P'], T['u'], T['s'], str(T['al']), str(T['be']), str(T['alB']), str(T['beB']), T['S']]


def parse_digits(T, w):
    """w = sequence of digits u^(al d+be) s ...  -> list of digits, or None"""
    u, s = T['u'], T['s']
    i, digs = 0, []
    while i < len(w):
        v = 0
        while w.startswith(u, i):
            i += len(u)
            v += 1
        if not w.startswith(s, i):
            return None
        i += len(s)
        if v < T['be'] or (v - T['be']) % T['al']:
            return None
        digs.append((v - T['be']) // T['al'])
    return digs


def recodings(tmpl):
    """template recodings that make zero digits representable / absorb suffix units:
    s = u^j s' -> s', be += j (then also be lowered to 0); S = u^j S' -> S', beB += j"""
    T = parse_template(tmpl)
    out = []
    u = T['u']
    s = T['s']
    j = 0
    while s.startswith(u) and len(s) > len(u):
        s = s[len(u):]
        j += 1
    S = T['S'] if T['S'] != '-' else ''
    jS = 0
    while S.startswith(u):
        S = S[len(u):]
        jS += 1
    for sj in sorted(set([0, j])):
        for bes in sorted(set([T['be'] + sj, 0])):
            for Sj in sorted(set([0, jS])):
                T2 = dict(T)
                if sj:
                    T2['s'] = T['s'][len(u) * sj:]
                T2['be'] = bes
                if Sj:
                    T2['S'] = (T['S'][len(u) * Sj:] or '-')
                    T2['beB'] = T['beB'] + Sj
                ts = tstr(T2)
                if ts != tmpl and ts not in out:
                    out.append(ts)
    return out


def variants(tmpl):
    """template variants: P split as P0 + digits (P0 empty or starting with 1). Most digits absorbed first.
    Returns [(template string, absorbed digits)]."""
    T = parse_template(tmpl)
    P = '' if T['P'] == '-' else T['P']
    out = []
    for cut in range(0, len(P) + 1):
        P0, rest = P[:cut], P[cut:]
        if P0 and P0[0] != '1':
            continue
        d = parse_digits(T, rest)
        if d is None:
            continue
        if not P0 and d and d[0] == 0:
            continue
        T2 = dict(T)
        T2['P'] = P0 if P0 else '-'
        out.append((tstr(T2), d))
    out.sort(key=lambda x: -len(x[1]))
    if not any(v[0] == tmpl for v in out):
        out.append((tmpl, []))
    return out


# --------------------------------------------------------------------------------------------- rk7 calls
class Prober:
    def __init__(self, machine, tmpl):
        self.m = machine
        self.tmpl = tmpl
        self.T = parse_template(tmpl)
        self.Pempty = self.T['P'] == '-'
        self.calls = 0
        self.cache = {}

    def run(self, args, inp=None, timeout=3600):
        p = subprocess.run([RK7] + args, input=inp, capture_output=True, text=True, creationflags=IDLE,
                           timeout=timeout)
        return p.stdout

    def trace(self, steps, maxk):
        out = self.run(['trace', self.m] + targs(self.T) + [str(steps), str(maxk)])
        ks, end = [], None
        for ln in out.splitlines():
            f = ln.split()
            if not f:
                continue
            if f[0] == 'K':
                ds = [] if f[2] == '-' else [int(x) for x in f[2].split(',')]
                ks.append((int(f[1]), ds, int(f[3]), int(f[4])))
            else:
                end = f
        return ks, end

    def probe(self, cfgs, N=3000000):
        """cfgs [(ds, a, b)] -> [('K', ds, a, b, steps) | ('H', steps) | ('T',)]"""
        todo = [c for c in cfgs if (tuple(c[0]), c[1], c[2], N) not in self.cache]
        todo = list(dict.fromkeys((tuple(c[0]), c[1], c[2]) for c in todo))
        if todo:
            inp = ''.join('%s %d %d\n' % (','.join(map(str, ds)) if ds else '-', a, b) for ds, a, b in todo)
            out = self.run(['probe', self.m] + targs(self.T) + [str(N)], inp)
            self.calls += 1
            res = []
            for ln in out.splitlines():
                f = ln.split()
                if not f:
                    continue
                if f[0] == 'K':
                    res.append(('K', [] if f[1] == '-' else [int(x) for x in f[1].split(',')], int(f[2]), int(f[3]),
                                int(f[4])))
                elif f[0] == 'H':
                    res.append(('H', int(f[1])))
                else:
                    res.append(('T',))
            while len(res) < len(todo):
                res.append(('T',))
            for c, r in zip(todo, res):
                self.cache[(c[0], c[1], c[2], N)] = r
        return [self.cache[(tuple(c[0]), c[1], c[2], N)] for c in cfgs]

    def follow(self, cfg, N=3000000, maxp=3):
        ds, a, b = cfg
        inp = '%s %d %d\n' % (','.join(map(str, ds)) if ds else '-', a, b)
        return self.run(['follow', self.m] + targs(self.T) + [str(N), str(maxp)], inp).strip().splitlines()


def norm(ds, Pempty):
    ds = list(ds)
    if Pempty:
        while ds and ds[0] == 0:
            ds.pop(0)
    return ds


# --------------------------------------------------------------------------------------------- fitting helpers
def fit_line(pts):
    """[(x, y)] -> (m, c) exact integer line through all points, or None"""
    if len(pts) < 2:
        return None
    (x0, y0), (x1, y1) = pts[0], pts[1]
    if x1 == x0 or (y1 - y0) % (x1 - x0):
        return None
    m = (y1 - y0) // (x1 - x0)
    c = y0 - m * x0
    return (m, c) if all(y == m * x + c for x, y in pts) else None


def aff(f, b):
    return f[0] * b + f[1]


class FitError(Exception):
    pass


def fit_D(P, ctx_list, B=range(0, 10)):
    """F0 from K(ctx; a; b) a = 1..3"""
    cf = [(ctx, a, b) for ctx in ctx_list for a in (1, 2, 3) for b in B]
    res = P.probe(cf)
    pts = {}
    bad = []
    for c, r in zip(cf, res):
        if r[0] == 'K' and norm(r[1], P.Pempty) == norm(c[0], P.Pempty) and r[2] == c[1] - 1:
            pts.setdefault(c[2], set()).add(r[3])
        else:
            bad.append((c, r[:4]))
    if any(len(v) > 1 for v in pts.values()):
        raise FitError('D: b-result depends on context/a')
    f = fit_line(sorted((b, v.pop()) for b, v in pts.items() if len(v) == 1)) if len(pts) >= 3 else None
    small = {}
    if f is None:
        raise FitError('D: no affine fit (%d bad)' % len(bad))
    for c, r in bad:
        small.setdefault(c[2], set()).add(r[0])
    return f, bad


def fit_R2(P, ctxs, B=range(0, 14)):
    """K(ctx+[d+1]; 0; b) -> K(ctx+[d]; A2(b); B2(b))"""
    cf, keys = [], []
    for ctx in ctxs:
        for b in B:
            cf.append((ctx, 0, b))
    res = P.probe(cf)
    byb = {}
    bad = []
    for c, r in zip(cf, res):
        want = norm(c[0][:-1] + [c[0][-1] - 1], P.Pempty)
        if r[0] == 'K' and norm(r[1], P.Pempty) == want:
            byb.setdefault(c[2], set()).add((r[2], r[3]))
        else:
            bad.append((c, r[:4]))
    if any(len(v) > 1 for v in byb.values()):
        raise FitError('R2 depends on context')
    bs = sorted(byb)
    # fit on the upper part of the window (small b may be exceptional)
    for lo in range(0, max(1, len(bs) - 4)):
        sub = bs[lo:]
        if len(sub) < 4:
            break
        fa = fit_line([(b, list(byb[b])[0][0]) for b in sub])
        fb = fit_line([(b, list(byb[b])[0][1]) for b in sub])
        if fa and fb:
            exc = [(b, list(byb[b])[0]) for b in bs[:lo]]
            return fa, fb, bad, exc
    raise FitError('R2: no affine fit')


def fit_borrow(P, k, b0, nb=10, ctx=(1, 2)):
    """K([1,2,0^k]; 0; b) for b = b0..b0+nb-1 -> entries of L affine, a', b' affine. Returns dict or raises."""
    ctx = list(ctx)
    cf = [(ctx + [0] * k, 0, b) for b in range(b0, b0 + nb)]
    r0 = P.probe(cf[:1], N=6000000)[0]
    if r0[0] != 'K':
        return None, [(b0, r0[0])]
    res = P.probe(cf, N=6000000)
    rows = []
    for c, r in zip(cf, res):
        if r[0] != 'K':
            return None, [(c[2], r[0])]
        ds = norm(r[1], P.Pempty)
        want0 = norm(ctx[:-1] + [ctx[-1] - 1], P.Pempty)
        if len(ds) != len(want0) + k or ds[:len(want0)] != want0:
            return None, [(c[2], 'X', r[1][:12], r[2], r[3])]
        rows.append((c[2], ds[len(want0):], r[2], r[3]))
    L = []
    for i in range(k):
        f = fit_line([(b, l[i]) for b, l, _, _ in rows])
        if f is None:
            return None, [('entry', i, [l[i] for _, l, _, _ in rows])]
        L.append(f)
    fa = fit_line([(b, a) for b, _, a, _ in rows])
    fb = fit_line([(b, bb) for b, _, _, bb in rows])
    if fa is None or fb is None:
        return None, [('ab', [(a, bb) for _, _, a, bb in rows])]
    return {'L': L, 'a': fa, 'b': fb}, None


def small_scan(P, cfgs_pred, N=3000000):
    """cfgs_pred = [(cfg, predicted ('K', ds, a, b) or None)] -> list of (cfg, literal) where literal != predicted"""
    res = P.probe([c for c, _ in cfgs_pred], N=N)
    out = []
    for (c, p), r in zip(cfgs_pred, res):
        if p is not None and r[0] == 'K' and norm(r[1], P.Pempty) == norm(p[1], P.Pempty) and r[2] == p[2] and r[3] == p[3]:
            continue
        out.append((c, r[:4]))
    return out


def fit_tail_pattern(Ls, k0):
    """Ls: {k: [entries (m,c)]} for k >= k0. Entry layout: pre (constants, top) + [x] + head + mid^* + end with x the
    only b-dependent entry (slope m, intercept x0 + x1 k). Returns dict or None."""
    ks = sorted(k for k in Ls if k >= k0)
    if len(ks) < 3:
        return None
    ias = set()
    for k in ks:
        nz = [i for i, e in enumerate(Ls[k]) if e[0] != 0]
        if len(nz) != 1:
            return None
        ias.add(nz[0])
    if len(ias) != 1:
        return None
    ia = ias.pop()
    pres = set(tuple(e[1] for e in Ls[k][:ia]) for k in ks)
    if len(pres) != 1:
        return None
    pre = list(pres.pop())
    m = Ls[ks[0]][ia][0]
    if any(Ls[k][ia][0] != m for k in ks):
        return None
    fc = fit_line([(k, Ls[k][ia][1]) for k in ks])
    if fc is None:
        return None
    tv = {k: [e[1] for e in Ls[k][ia + 1:]] for k in ks}
    for hl in range(0, 3):
        for el in range(0, 3):
            ok = True
            mid = None
            head = end = None
            for k in ks:
                t = tv[k]
                if len(t) < hl + el + 1:
                    ok = False
                    break
                h, e, md = t[:hl], t[len(t) - el:] if el else [], t[hl:len(t) - el]
                if head is None:
                    head, end = h, e
                if h != head or e != end or len(set(md)) != 1:
                    ok = False
                    break
                if mid is None:
                    mid = md[0]
                elif md[0] != mid:
                    ok = False
                    break
            if ok:
                return {'pre': pre, 'm': m, 'x1': fc[0], 'x0': fc[1], 'head': head, 'mid': mid, 'end': end,
                        'kmin': ia + hl + el + 2}
    return None


def period_of(seq, maxp=12):
    for p in range(1, maxp + 1):
        if all(seq[i] == seq[i + p] for i in range(len(seq) - p)):
            return p
    return None


def rle(L):
    out = []
    for x in L:
        if out and out[-1][0] == x:
            out[-1][1] += 1
        else:
            out.append([x, 1])
    return out


def list_struct(L):
    """split L into (pre, mid digit, count, suf) at its longest run (count >= 1), or (L, None, 0, [])"""
    R = rle(L)
    if not R:
        return [], None, 0, []
    i = max(range(len(R)), key=lambda j: (R[j][1], -j))
    if R[i][1] < 3:
        return list(L), None, 0, []
    pre = [x for v, c in R[:i] for x in [v] * c]
    suf = [x for v, c in R[i + 1:] for x in [v] * c]
    return pre, R[i][0], R[i][1], suf


def e_to_V(E, m1, c1):
    """E fitted on the pre-exhaustion accumulator b (probe K(0^n;1;b), V = F0(b) = m1 b + c1) -> E on V.
    Classes of V outside the image of F0 become ('X',) (impossible)."""
    if E is None or m1 <= 0:
        return None
    p, cls = E
    pV = m1 * p
    out = {}
    for cV in range(pV):
        if (cV - c1) % m1:
            out[cV] = ('X',)
            continue
        # V = m1 b + c1 with b = c (mod p): cV = m1 c + c1 (mod m1 p)
        c = None
        for cc in range(p):
            if (m1 * cc + c1 - cV) % pV == 0:
                c = cc
                break
        r = cls[c]
        if r[0] != 'K':
            out[cV] = r
            continue
        delta = (m1 * c + c1 - cV) // pV          # t_b = t_V - delta
        d = dict(r[1])

        def sh(f):
            al, be = f
            return (al, be - al * delta)
        nd = {}
        for k, v in d.items():
            if k in ('pre', 'suf', 'mid'):
                nd[k] = v
            elif k == 'fixed':
                nd[k] = [sh(e) for e in v]
            else:
                nd[k] = sh(v)
        out[cV] = ('K', nd)
    return (pV, out)


def fit_E(P, n, B0, nb=48, N=12000000, maxp=16, a0=0, probe=None, out_pempty=None):
    """exhaustion probes E(b), b = B0..B0+nb-1, for n leading zero digits (P nonempty) or the empty list.
    Per class c mod p, with t = (b - c) // p, every number is affine in t:
      ('H',) | ('T',) | ('K', {'pre': [..], 'mid': v, 'cnt': (al, be), 'suf': [..], 'a': (al, be), 'b': (al, be)})
      | ('K', {'fixed': [(al, be)...], 'a':.., 'b':..})
    Returns (pattern, (p, classes) or None, raw results)."""
    ds = [] if P.Pempty else [0] * n
    bs = list(range(B0, B0 + nb))
    pr = probe or (lambda cf: P.probe(cf, N=N))
    first = pr([(ds, a0, b) for b in bs[:12]])
    if all(r[0] == 'T' for r in first):
        return 'T' * 12, (1, {0: ('T',)}), first
    res = first + pr([(ds, a0, b) for b in bs[12:]])
    if out_pempty is not None:
        class _PP:
            Pempty = out_pempty
        P = _PP
    if a0 == 1:
        # the plain D step K(0^n;1;b) -> K(0^n;0;F0 b) means K(0^n;0;.) is itself a K-moment: no composite
        res = [('D',) if (r[0] == 'K' and norm(r[1], P.Pempty) == norm(ds, P.Pempty) and r[2] == 0) else r
               for r in res]
    pat = ''.join(r[0] for r in res)
    best = None
    for p in range(1, maxp + 1):
        cls = {}
        ok = True
        for c in range(p):
            pts = [((b - c) // p, r) for b, r in zip(bs, res) if b % p == c]
            if len(pts) < 3:
                ok = False
                break
            kinds = set(r[0] for _, r in pts)
            if len(kinds) != 1:
                ok = False
                break
            kd = kinds.pop()
            if kd != 'K':
                cls[c] = (kd,)
                continue
            sts = [(t, list_struct(norm(r[1], P.Pempty)), r[2], r[3]) for t, r in pts]
            pre = set(tuple(s[0]) for _, s, _, _ in sts)
            suf = set(tuple(s[3]) for _, s, _, _ in sts)
            mid = set(s[1] for _, s, _, _ in sts)
            fa = fit_line([(t, a) for t, _, a, _ in sts])
            fb = fit_line([(t, bb) for t, _, _, bb in sts])
            if len(pre) == 1 and len(suf) == 1 and len(mid) == 1 and None not in mid:
                cnt = fit_line([(t, s[2]) for t, s, _, _ in sts])
                if cnt and fa and fb:
                    cls[c] = ('K', {'pre': list(pre.pop()), 'mid': mid.pop(), 'cnt': cnt, 'suf': list(suf.pop()),
                                    'a': fa, 'b': fb})
                    continue
            lens = set(len(norm(r[1], P.Pempty)) for _, r in pts)
            if len(lens) == 1 and fa and fb:
                ln = lens.pop()
                ent = [fit_line([(t, norm(r[1], P.Pempty)[i]) for t, r in pts]) for i in range(ln)]
                if all(ent):
                    cls[c] = ('K', {'fixed': ent, 'a': fa, 'b': fb})
                    continue
            ok = False
            break
        if ok:
            best = (p, cls)
            break
    return pat, best, res


# --------------------------------------------------------------------------------------------- full fit
def fit_rules(P, KF=7, Bwin=12):
    """Fit all rules for prober P. Returns dict R (raises FitError on failure)."""
    R = {'tmpl': P.tmpl, 'Pempty': P.Pempty}
    ctxD = [[2, 1], [1, 0, 3], [3, 2]]
    R['F0'], badD = fit_D(P, ctxD)
    R['smallD'] = sorted(set((c[2], r[0]) for c, r in badD))
    fa, fb, badR2, excR2 = fit_R2(P, [[2, 1], [1, 3], [1, 0, 2]])
    R['A2'], R['B2'] = fa, fb
    R['excR2'] = excR2
    R['smallR2'] = sorted(set((c[2], r[0]) for c, r in badR2))
    # borrows: find a b-window where each k fits; record small-b behaviour below it
    R['B'] = {}
    R['smallB'] = {}
    for k in range(1, KF + 1):
        got = None
        for b0 in (3 * k + 6, 6 * k + 10, 12 * k + 20):
            f, why = fit_borrow(P, k, b0, nb=Bwin)
            if f:
                got = f
                # second window check (affine must persist)
                f2, _ = fit_borrow(P, k, b0 + 37, nb=4)
                if f2 is None or f2 != f:
                    got = None
                    continue
                break
        if got is None:
            raise FitError('B%d: no affine fit (%s)' % (k, why))
        R['B'][k] = got
        b0 = 3 * k + 6
        # small b scan for k: b = 0..b0-1, predicted by the affine rule
        pred = []
        for b in range(0, b0):
            L = [aff(e, b) for e in got['L']]
            pa, pb = aff(got['a'], b), aff(got['b'], b)
            p = ('K', [1, 1] + L, pa, pb) if min(L + [pa, pb]) >= 0 else None
            pred.append((([1, 2] + [0] * k, 0, b), p))
        R['smallB'][k] = [(c[2], r[0], (r[1][:8] if r[0] == 'K' else None)) for c, r in small_scan(P, pred)]
    # extrapolation in k
    Ls = {k: R['B'][k]['L'] for k in R['B']}
    pat = None
    for k0 in (2, 3, 4):
        pat = fit_tail_pattern(Ls, k0)
        if pat:
            pat['k0'] = max(k0, pat['kmin'])
            break
    if pat is None:
        raise FitError('borrow tails: no head/mid/end pattern')
    ab = set((tuple(R['B'][k]['a']), tuple(R['B'][k]['b'])) for k in R['B'] if k >= pat['k0'])
    if len(ab) != 1:
        raise FitError('borrow a/b vary with k: %s' % sorted(ab)[:4])
    a_, b_ = ab.pop()
    pat['a'], pat['b'] = list(a_), list(b_)
    R['Bpat'] = pat
    R['MB'] = None
    if not P.Pempty:
        kinds = marker_scan(P)
        R['mscan'] = ''.join(kinds[n] for n in sorted(kinds))
        top = max(kinds)
        if kinds[top] == 'S':
            nE = top
            while nE > 0 and kinds[nE] == 'S':
                nE -= 1
            if kinds[nE] == 'S':
                R['MBwhy'] = 'all levels shrink (scan %s)' % R['mscan']
            else:
                mb, why = fit_MB(P, nE)
                if mb:
                    R['MB'], R['MBpat'], R['smallMB'] = mb
                    R['nE'] = nE
                else:
                    R['MBwhy'] = why
        else:
            R['MBwhy'] = 'no marker staircase (scan %s)' % R['mscan']
    return R


def marker_scan(P, nmax=9):
    """kinds of K(0^n;0;b) for n = 0..nmax at two b: 'S' (list shrinks to n-1 entries), 'K', 'H', 'T', 'M' (mixed)"""
    kinds = {}
    for n in range(0, nmax + 1):
        res = P.probe([([0] * n, 0, b) for b in (3 * n + 40, 3 * n + 41)], N=8000000)
        ks = set()
        for r in res:
            if r[0] == 'K':
                ks.add('S' if len(r[1]) == n - 1 else 'K')
            else:
                ks.add(r[0])
        kinds[n] = ks.pop() if len(ks) == 1 else 'M'
    return kinds


def fit_MB(P, nE, nmax=7, Bwin=12):
    """marker borrows (P nonempty) above the true exhaustion level nE: K(0^n; 0; b) -> K(L_n(b); a; b) with
    |L_n| = n - 1, n = nE+1 .. nE+nmax. Returns ((MB {n: {'L','a','b'}}, MBpat over k = n-1, smallMB), None) or
    (None, reason)."""
    MB, small = {}, {}
    for n in range(nE + 1, nE + nmax + 1):
        got = None
        why = None
        for b0 in (3 * n + 6, 6 * n + 10, 12 * n + 20):
            cf = [([0] * n, 0, b) for b in range(b0, b0 + Bwin)]
            r0 = P.probe(cf[:1], N=6000000)[0]
            if r0[0] != 'K' or len(r0[1]) != n - 1:
                why = (n, b0, r0[0], (r0[1][:6], len(r0[1])) if r0[0] == 'K' else None)
                continue
            res = P.probe(cf, N=6000000)
            if any(r[0] != 'K' or len(r[1]) != n - 1 for r in res):
                why = (n, b0, 'mixed')
                continue
            L = []
            ok = True
            for i in range(n - 1):
                f = fit_line([(c[2], r[1][i]) for c, r in zip(cf, res)])
                if f is None:
                    ok = False
                    break
                L.append(f)
            fa = fit_line([(c[2], r[2]) for c, r in zip(cf, res)])
            fb = fit_line([(c[2], r[3]) for c, r in zip(cf, res)])
            if not ok or fa is None or fb is None:
                why = (n, b0, 'nonaffine')
                continue
            got = {'L': L, 'a': fa, 'b': fb}
            b0used = b0
            break
        if got is None:
            return None, 'MB n=%d: %s' % (n, why)
        MB[n] = got
        pred = []
        for b in range(0, b0used):
            Lv = [aff(e, b) for e in got['L']]
            pa, pb = aff(got['a'], b), aff(got['b'], b)
            pred.append((([0] * n, 0, b), ('K', Lv, pa, pb) if min(Lv + [pa, pb]) >= 0 else None))
        small[n] = [(c[2], r[0], (r[1][:8] if r[0] == 'K' else None)) for c, r in small_scan(P, pred)]
    Ls = {n - 1: MB[n]['L'] for n in MB if n >= 2}
    pat = None
    for k0 in sorted(set([max(2, nE + 1), max(3, nE + 2), max(4, nE + 3)])):
        pat = fit_tail_pattern(Ls, k0)
        if pat:
            pat['k0'] = max(k0, pat['kmin'])
            break
    if pat is None:
        return None, 'MB tails: no pattern'
    ab = set((tuple(MB[n]['a']), tuple(MB[n]['b'])) for n in MB if n - 1 >= pat['k0'])
    if len(ab) != 1:
        return None, 'MB a/b vary with n'
    a_, b_ = ab.pop()
    pat['a'], pat['b'] = list(a_), list(b_)
    return (MB, pat, small), None


def mb_rule(R, n):
    """marker borrow with n zero digits -> (L, a, b)"""
    if n in R['MB']:
        x = R['MB'][n]
        return x['L'], x['a'], x['b']
    return pat_list(R['MBpat'], n - 1)


def pat_list(p, k):
    """entries of a pattern level with k positions: pre + [x] + head + mid^* + end"""
    pre = p.get('pre', [])
    nmid = k - 1 - len(pre) - len(p['head']) - len(p['end'])
    if nmid < 0:
        raise FitError('pattern undefined at k=%d' % k)
    L = [(0, v) for v in pre] + [(p['m'], p['x0'] + p['x1'] * k)] + [(0, v) for v in p['head']] +         [(0, p['mid'])] * nmid + [(0, v) for v in p['end']]
    return L, tuple(p['a']), tuple(p['b'])


def borrow_rule(R, k):
    """(L entries [(m,c)], a (m,c), b (m,c)) for a borrow over k zeros"""
    if k in R['B']:
        x = R['B'][k]
        return x['L'], x['a'], x['b']
    return pat_list(R['Bpat'], k)


def rule_next(R, cfg):
    """one K-level step on an exact configuration (fitted rules, large-b forms). ('K', ds, a, b, rule) / ('E', n, b)"""
    ds, a, b = cfg
    if a > 0:
        return ('K', list(ds), a - 1, aff(R['F0'], b), 'D')
    if ds and ds[-1] > 0:
        nd = list(ds)
        nd[-1] -= 1
        return ('K', norm(nd, R['Pempty']), aff(R['A2'], b), aff(R['B2'], b), 'R2')
    j = len(ds) - 1
    while j >= 0 and ds[j] == 0:
        j -= 1
    if j < 0:
        if R.get('MB') and len(ds) > R.get('nE', 0):
            L, fa, fb = mb_rule(R, len(ds))
            return ('K', [aff(e, b) for e in L], aff(fa, b), aff(fb, b), 'MB%d' % len(ds))
        return ('E', len(ds), b)
    k = len(ds) - 1 - j
    L, fa, fb = borrow_rule(R, k)
    nd = list(ds[:j]) + [ds[j] - 1] + [aff(e, b) for e in L]
    return ('K', norm(nd, R['Pempty']), aff(fa, b), aff(fb, b), 'B%d' % k)


def check_random(P, R, n=80, seed=1, kmax=12, N=6000000):
    """random literal configurations vs rule_next (borrows over up to kmax zeros forced in 60%)"""
    rnd = random.Random(seed)
    cf, pr = [], []
    for _ in range(n * 3):
        if len(cf) >= n:
            break
        if rnd.random() < 0.6:
            k = rnd.randint(1, kmax)
            ds = [rnd.randint(1, 4)] + [rnd.randint(0, 4) for _ in range(rnd.randint(0, 2))] + [rnd.randint(1, 4)] + [0] * k
            a, b = 0, rnd.randint(3 * k + 6, 3 * k + 30)
        else:
            m = rnd.randint(1, 5)
            ds = [rnd.randint(1, 4)] + [rnd.randint(0, 4) for _ in range(m - 1)]
            a, b = rnd.randint(0, 6), rnd.randint(4, 20)
        if R.get('MB') and rnd.random() < 0.15:
            n = rnd.randint(R.get('nE', 0) + 1, R.get('nE', 0) + kmax)
            ds, a, b = [0] * n, 0, rnd.randint(3 * n + 6, 3 * n + 30)
        nx = rule_next(R, (ds, a, b))
        if nx[0] != 'K' or min(nx[1] + [nx[2], nx[3]]) < 0:
            continue
        cf.append((ds, a, b))
        pr.append(nx)
    res = P.probe(cf, N=N)
    ok, miss, nt = 0, [], 0
    for c, p, r in zip(cf, pr, res):
        if r[0] == 'K' and norm(r[1], P.Pempty) == norm(p[1], P.Pempty) and r[2] == p[2] and r[3] == p[3]:
            ok += 1
        elif r[0] == 'T':
            nt += 1
        else:
            miss.append((c, p[4], r[:4]))
    return ok, len(cf), nt, miss
