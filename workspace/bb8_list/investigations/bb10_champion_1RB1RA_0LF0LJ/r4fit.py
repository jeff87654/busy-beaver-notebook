"""Fit the used-up-list rule R4 of a Kd-family machine:  Kd [] 0 b  ->  HALT  or  Kd ds' a' b'.

For a period p in (1, 2, 4, 8) and each class b = p*n + r, the outcomes on a fitting window must be either all HALT
(ones linear in n) or all K with  ds' = P + B^(alpha*n + beta) + S  (items of P, B, S are digits linear in n) and
a', b' linear in n.  Templates are fitted on one window and validated on a second, disjoint window (exact literal runs).
Fails loudly (returns None + reason) when no template fits.
"""
from fractions import Fraction as F
from kd import run_next


R4PROBE = __import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)), 'r4probe.exe')


def probe_fast(M, b0, b1, mul=4, add=5000):
    """C++ prober (r4probe.exe), same outcome format as probe(); None if the executable is missing"""
    import os
    import subprocess
    if not os.path.exists(R4PROBE):
        return None
    r = subprocess.run([R4PROBE, M, str(b0), str(b1), str(mul), str(add)], capture_output=True, text=True, timeout=3600)
    out = {}
    for line in r.stdout.splitlines():
        f = line.split()
        if f[0] == 'K':
            b = int(f[1])
            ds = tuple(int(x) for x in f[5].split(',')) if len(f) > 5 else ()
            out[b] = ('K', ds, int(f[3]), int(f[4]), int(f[2]))
        elif f[0] == 'HALT':
            out[int(f[1])] = ('HALT', int(f[5]), (f[3], int(f[4])), int(f[2]))
        elif f[0] == 'TIMEOUT':
            out[int(f[1])] = ('TIMEOUT', int(f[2]))
        else:
            raise ValueError('r4probe: unparsed line %r' % line)
    if sorted(out) != list(range(b0, b1)):
        raise ValueError('r4probe: missing outcomes for %s' % M)
    return out


def probe(M, bs, N=None):
    bs = list(bs)
    if N is None and bs == list(range(bs[0], bs[-1] + 1)):
        fast = probe_fast(M, bs[0], bs[-1] + 1)
        if fast is not None:
            return fast
    out = {}
    for b in bs:
        lim = N or (4 * (b + 4) ** 2 + 5000)
        r = run_next(M, (), 0, b, N=lim)
        if r[0] == 'K':
            out[b] = ('K', r[2][0], r[2][1], r[2][2], r[1])
        elif r[0] == 'HALT':
            out[b] = ('HALT', r[3].ones(), r[2], r[1])
        else:
            out[b] = ('TIMEOUT', r[1])
    return out


def linfit(pts):
    """pts: list of (n, value) -> (c1, c0) Fractions with value = c1*n + c0 for all points, else None"""
    if len(pts) < 2:
        return None
    (n0, v0), (n1, v1) = pts[0], pts[1]
    c1 = F(v1 - v0, n1 - n0)
    c0 = v0 - c1 * n0
    if all(c1 * n + c0 == v for n, v in pts):
        return (c1, c0)
    return None


def lin_str(c):
    c1, c0 = c
    if c1 == 0:
        return str(c0)
    s = ('%sn' % c1) if c1 != 1 else 'n'
    if c0:
        s += ('%+d' % c0) if c0.denominator == 1 else ('+%s' % c0)
    return s


def fit_items(rows):
    """rows: list of (n, list_of_digits), all of equal length -> list of integer linear fits per position, or None"""
    if not rows:
        return []
    L = len(rows[0][1])
    if any(len(d) != L for n, d in rows):
        return None
    out = []
    for i in range(L):
        pts = {}
        for n, d in rows:
            if n in pts and pts[n] != d[i]:
                return None
            pts[n] = d[i]
        pl = sorted(pts.items())
        if len(pl) == 1:
            c = (F(0), F(pl[0][1]))
        else:
            c = linfit(pl)
        if c is None or c[0].denominator != 1 or c[1].denominator != 1:
            return None
        out.append(c)
    return out


def fit_list(seq):
    """seq: list of (n, ds) -> template dict or None"""
    lens = [(n, len(ds)) for n, ds in seq]
    lf = linfit(lens)
    if lf is None or lf[0].denominator != 1:
        return None
    delta = int(lf[0])
    nA, dsA = seq[0]
    LA = len(dsA)
    if delta == 0:
        it = fit_items(seq)
        if it is None:
            return None
        return {'P': it, 'B': [], 'S': [], 'alpha': 0, 'beta': 0}
    if delta < 0:
        return None
    for blen in range(1, delta + 1):
        if delta % blen:
            continue
        alpha = delta // blen
        for fix in range(0, LA + 1):              # fix = plen + slen
            rest = LA - fix
            if rest < 0 or rest % blen:
                continue
            cA = rest // blen
            beta = cA - alpha * nA
            for plen in range(0, fix + 1):
                slen = fix - plen
                Prows, Srows, Brows = [], [], []
                ok = True
                for n, ds in seq:
                    c = alpha * n + beta
                    if c < 1:
                        ok = False
                        break
                    Prows.append((n, ds[:plen]))
                    Srows.append((n, ds[len(ds) - slen:] if slen else ()))
                    for k in range(c):
                        Brows.append((n, ds[plen + k * blen: plen + (k + 1) * blen]))
                if not ok:
                    continue
                P = fit_items(Prows)
                S = fit_items(Srows) if P is not None else None
                B = fit_items(Brows) if S is not None else None
                if B is None:
                    continue
                return {'P': P, 'B': B, 'S': S, 'alpha': alpha, 'beta': beta}
    return None


def tmpl_eval(t, n):
    ev = lambda c: int(c[0] * n + c[1])
    cnt = t['alpha'] * n + t['beta']
    ds = [ev(c) for c in t['P']] + [ev(c) for c in t['B']] * cnt + [ev(c) for c in t['S']]
    while ds and ds[-1] == 0:
        ds.pop()
    return tuple(ds)


def tmpl_str(t):
    s = lambda items: ','.join(lin_str(c) for c in items)
    parts = []
    if t['P']:
        parts.append(s(t['P']))
    if t['B']:
        parts.append('(' + s(t['B']) + ')^(' + lin_str((F(t['alpha']), F(t['beta']))) + ')')
    if t['S']:
        parts.append(s(t['S']))
    return '[' + ','.join(parts) + ']'


def fit_class(outs):
    """outs: list of (n, outcome) for one residue class -> rule dict or None"""
    kinds = set(o[0] for n, o in outs)
    if kinds == {'HALT'}:
        c = linfit([(n, o[1]) for n, o in outs])
        st = set(o[2] for n, o in outs)
        if c is None or len(st) != 1:
            return None
        return {'kind': 'HALT', 'ones': c, 'at': st.pop()}
    if kinds == {'TIMEOUT'}:
        return {'kind': 'TIMEOUT'}          # no return to the Kd shape within the probe limit (runaway / very slow)
    if kinds == {'K'}:
        t = fit_list([(n, o[1]) for n, o in outs])
        ca = linfit([(n, o[2]) for n, o in outs])
        cb = linfit([(n, o[3]) for n, o in outs])
        if t is None or ca is None or cb is None:
            return None
        return {'kind': 'K', 'list': t, 'a': ca, 'b': cb}
    return None


def rule_predict(rule, n):
    if rule['kind'] == 'TIMEOUT':
        return ('TIMEOUT',)
    if rule['kind'] == 'HALT':
        return ('HALT', int(rule['ones'][0] * n + rule['ones'][1]))
    return ('K', tmpl_eval(rule['list'], n), int(rule['a'][0] * n + rule['a'][1]), int(rule['b'][0] * n + rule['b'][1]))


def fit_r4(M, fit_lo=16, fit_hi=80, val_hi=144, outs=None):
    """returns (period p, {r: rule}, outs) or (None, reason, outs)"""
    outs = outs or probe(M, range(0, val_hi))
    for p in (1, 2, 3, 4, 6, 8, 12):
        rules = {}
        ok = True
        for r in range(p):
            fit = [((b - r) // p, outs[b]) for b in range(fit_lo, fit_hi) if b % p == r]
            rule = fit_class(fit)
            if rule is None:
                ok = False
                break
            for b in range(fit_hi, val_hi):           # validation window
                if b % p != r:
                    continue
                n = (b - r) // p
                pr = rule_predict(rule, n)
                o = outs[b]
                if pr[0] == 'HALT':
                    good = o[0] == 'HALT' and o[1] == pr[1]
                elif pr[0] == 'TIMEOUT':
                    good = o[0] == 'TIMEOUT'
                else:
                    good = o[0] == 'K' and (o[1], o[2], o[3]) == pr[1:]
                if not good:
                    ok = False
                    break
            if not ok:
                break
            rules[r] = rule
        if ok:
            return p, rules, outs
    kinds = {}
    for b in range(fit_lo, val_hi):
        kinds[outs[b][0]] = kinds.get(outs[b][0], 0) + 1
    return None, 'no R4 template with period in 1,2,3,4,6,8,12 (outcomes %s)' % kinds, outs


def rule_str(rule):
    if rule['kind'] == 'TIMEOUT':
        return 'NO-RETURN(no Kd configuration within the probe limit)'
    if rule['kind'] == 'HALT':
        return 'HALT(ones=%s at %s%d)' % (lin_str(rule['ones']), rule['at'][0], rule['at'][1])
    return 'Kd %s a=%s b=%s' % (tmpl_str(rule['list']), lin_str(rule['a']), lin_str(rule['b']))


if __name__ == '__main__':
    import sys
    M = sys.argv[1]
    p, rules, outs = fit_r4(M)
    if p is None:
        print('FAIL', rules)
    else:
        for r in range(p):
            print('b = %dn+%d: %s' % (p, r, rule_str(rules[r])))
