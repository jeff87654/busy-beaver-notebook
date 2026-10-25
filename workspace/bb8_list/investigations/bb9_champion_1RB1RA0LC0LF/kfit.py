"""Fit-then-verify: read off a machine's K-family rules from literal probes, then check them on the full grid.

    python kfit.py TM [TM ...] [--grid] [--N steps] [--shape STATE,SUFFIX] [--params]
    (--params prints the fitted rules as JSON, the input of ktraj.js)

Generalized K rules (b >= 1; k = number of trailing zero digits; everything linear in b):
  R1  K(ds; a+1; b)              -> K(ds; a; m1 b + c1)
  R2  K(.., x+1; 0; b)           -> K(.., x; m2 b + c2; b2)
  R3  K(.., y+1, 0^k; 0; b)      -> K(.., y, m3 b + c3 - k, 1^(k-1); a3; b3)      for 1 <= k < kh(b)
  H   k = kh(b) = mh b + ch      -> halts (undefined transition)
  R4  K(; 0; b)                  -> K(P, 1^(m4 b + c4); a4; b4)
The parent 1RB1RA_..._1LB0RD_0LH1LF_1RF--- has m=4, c1=4, c2=3, b2=1, c3=3, a3=b3=1, kh=4b+1, R4=(2,1^(4b)),1,1.

Probes: R1 from K(2;2;b), R2 from K(2;0;b), R3/H from K(1,2,0^k;0;b), R4 from K(;0;b), b = 1..5.
Each parameter is fitted on b = 1, 2 and must reproduce b = 3..5 (else the rule is reported as 'no fit' with the
raw observations).  With --grid, the fitted rules are then compared with the literal successor of every
configuration in kfam.grid() (1352 cases; R3big = k > kh(b), which is never reached in the parent, is only listed).

Also prints the safety conditions of the parent's non-halting argument (see neighbors_F1.md, "General argument").
"""
import sys
from kfam import run_next, grid, show, trailing_zeros, strip, kind_of, set_shape

BS = range(1, 6)


def lin_fit(vals):
    """vals: dict b -> int. Fit m b + c on b=1,2 and verify on the rest."""
    bs = sorted(vals)
    b0, b1 = bs[0], bs[1]
    m = (vals[b1] - vals[b0]) // (b1 - b0)
    c = vals[b0] - m * b0
    if all(vals[b] == m * b + c for b in bs):
        return (m, c)
    return None


def fit(tm, N=10 ** 6):
    P = {}
    raw = {}
    # R1
    o = {b: run_next(tm, (2,), 2, b, N=N) for b in BS}
    raw['R1'] = o
    if all(v[0] == 'K' and v[2][0] == (2,) and v[2][1] == 1 for v in o.values()):
        f = lin_fit({b: v[2][2] for b, v in o.items()})
        if f:
            P['m1'], P['c1'] = f
    # R2
    o = {b: run_next(tm, (2,), 0, b, N=N) for b in BS}
    raw['R2'] = o
    if all(v[0] == 'K' and v[2][0] == (1,) for v in o.values()):
        f = lin_fit({b: v[2][1] for b, v in o.items()})
        bb = set(v[2][2] for v in o.values())
        if f and len(bb) == 1:
            P['m2'], P['c2'] = f
            P['b2'] = bb.pop()
    # R3 and halting boundary
    kh = {}
    r3 = {}
    r3raw = {}
    for b in BS:
        if b > 4:
            break
        for k in range(1, 8 * b + 8):
            v = run_next(tm, (1, 2) + (0,) * k, 0, b, N=N)
            r3raw[(b, k)] = v
            if v[0] == 'HALT':
                kh[b] = k
                break
            if v[0] != 'K':
                break
            ds, a, bb = v[2]
            if len(ds) == 2 + k and ds[:2] == (1, 1) and ds[3:] == (1,) * (k - 1):
                r3[(b, k)] = (ds[2] + k, a, bb)
            else:
                break
    raw['R3'] = r3raw
    if r3:
        consts = set((x[1], x[2]) for x in r3.values())
        byb = {}
        for (b, k), x in r3.items():
            byb.setdefault(b, set()).add(x[0])
        if len(consts) == 1 and all(len(s) == 1 for s in byb.values()) and len(byb) >= 2:
            f = lin_fit({b: s.pop() for b, s in byb.items()}) if len(byb) >= 3 else None
            if f:
                P['m3'], P['c3'] = f
                P['a3'], P['b3'] = consts.pop()
    if len(kh) >= 2:
        f = lin_fit(kh) if len(kh) >= 3 else None
        if f:
            P['mh'], P['ch'] = f
    raw['kh'] = kh
    # R4
    o = {b: run_next(tm, (), 0, b, N=N) for b in BS}
    raw['R4'] = o
    if all(v[0] == 'K' for v in o.values()):
        fits = {}
        for b, v in o.items():
            ds, a0, b0 = v[2]
            n = 0
            while n < len(ds) and ds[len(ds) - 1 - n] == 1:
                n += 1
            fits[b] = (tuple(ds[:len(ds) - n]), n, a0, b0)
        pref = set((x[0], x[2], x[3]) for x in fits.values())
        if len(pref) == 1:
            f = lin_fit({b: x[1] for b, x in fits.items()})
            if f:
                P['P'], P['a4'], P['b4'] = pref.pop()
                P['m4'], P['c4'] = f
    return P, raw


def rule_text(P):
    out = []
    g = lambda k: P.get(k, '?')
    out.append('R1: b -> %sb%+d' % (g('m1'), g('c1')) if 'm1' in P else 'R1: no fit')
    out.append('R2: a = %sb%+d, b = %s' % (g('m2'), g('c2'), g('b2')) if 'm2' in P else 'R2: no fit')
    out.append('R3: refill %sb%+d-k, a=%s b=%s' % (g('m3'), g('c3'), g('a3'), g('b3')) if 'm3' in P else 'R3: no fit')
    out.append('H: k = %sb%+d' % (g('mh'), g('ch')) if 'mh' in P else 'H: no fit')
    out.append('R4: (%s1^(%sb%+d)); %s; %s' % (''.join('%d,' % d for d in P['P']), g('m4'), g('c4'), g('a4'), g('b4'))
               if 'm4' in P else 'R4: no fit')
    return ' | '.join(out)


def predict(P, ds, a, b):
    ds = list(ds)
    if a >= 1:
        nb = P['m1'] * b + P['c1']
        if not ds and a == 1:
            return predict(P, (), 0, nb)
        return ('K', (tuple(ds), a - 1, nb))
    k = trailing_zeros(ds)
    if k == len(ds):
        return ('K', (strip(tuple(P['P']) + (1,) * (P['m4'] * b + P['c4'])), P['a4'], P['b4']))
    i = len(ds) - 1 - k
    if k == 0:
        ds[-1] -= 1
        return ('K', (strip(ds), P['m2'] * b + P['c2'], P['b2']))
    kh = P['mh'] * b + P['ch']
    if k < kh:
        ds[i] -= 1
        ds = ds[:i + 1] + [P['m3'] * b + P['c3'] - k] + [1] * (k - 1)
        return ('K', (strip(ds), P['a3'], P['b3']))
    if k == kh:
        return ('HALT',)
    return None


def safety(P):
    """Conditions used by the parent's argument (EX/IN/CH lemmas), for all b >= 1:
    (s1) R1 grows b:            m1 b + c1 >= b + 1
    (s2) R2 refill >= b:        m2 b + c2 >= b   (so R1iter after R2 ends with B >= b + 1 when b2 = 1)
    (s3) R3 refill after k<b:   m3 b + c3 - k >= b + 1 for k <= b - 1, i.e. (m3-1) b + c3 >= b ... checked as
                                 m3 b + c3 - (b - 1) >= 2
    (s4) halting boundary out of reach: kh(b) > b - 1 for all b (resets have k <= b - 1)
    (s5) a3 = b3 = b2 = 1 (the template's shape; otherwise the proof needs adapting)"""
    need = ['m1', 'c1', 'm2', 'c2', 'b2', 'm3', 'c3', 'a3', 'b3', 'mh', 'ch']
    if any(k not in P for k in need):
        return None
    res = {}
    rng = range(1, 200)
    res['s1'] = all(P['m1'] * b + P['c1'] >= b + 1 for b in rng)
    res['s2'] = all(P['m2'] * b + P['c2'] >= b for b in rng)
    res['s3'] = all(P['m3'] * b + P['c3'] - (b - 1) >= 2 for b in rng)
    res['s4'] = all(P['mh'] * b + P['ch'] > b - 1 for b in rng)
    res['s5'] = P['a3'] == P['b3'] == P['b2'] == 1
    return res


def main():
    if '--shape' in sys.argv:          # e.g. --shape F,0  (state, suffix) for 0^inf ... 1^a 0 1^b 0 F> 0^inf
        q, suf = sys.argv[sys.argv.index('--shape') + 1].split(',')
        set_shape(q, suf)
        sys.argv.remove(q + ',' + suf)
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    N = int(sys.argv[sys.argv.index('--N') + 1]) if '--N' in sys.argv else 10 ** 6
    if '--N' in sys.argv:
        args.remove(str(N))
    for tm in args:
        P, raw = fit(tm, N)
        print(tm)
        print('  ' + rule_text(P))
        if 'm1' not in P:
            print('  R1 raw:', [(b, show(v[2]) if v[0] == 'K' else v[:3]) for b, v in raw['R1'].items()])
        if 'm2' not in P:
            print('  R2 raw:', [(b, show(v[2]) if v[0] == 'K' else v[:3]) for b, v in raw['R2'].items()])
        if 'm3' not in P or 'mh' not in P:
            print('  R3 raw:', [(bk, show(v[2]) if v[0] == 'K' else v[:3]) for bk, v in list(raw['R3'].items())[:12]])
            print('  kh:', raw['kh'])
        if 'm4' not in P:
            print('  R4 raw:', [(b, show(v[2]) if v[0] == 'K' else v[:3]) for b, v in raw['R4'].items()])
        s = safety(P)
        print('  safety:', s)
        if '--params' in sys.argv:
            import json
            print('  params:', json.dumps({k: (list(v) if isinstance(v, tuple) else v) for k, v in P.items()},
                                          separators=(',', ':')))
        if '--grid' in sys.argv and all(k in P for k in ('m1', 'm2', 'm3', 'mh', 'm4')):
            stats = {}
            bad = []
            for ds, a, b in grid():
                r = run_next(tm, ds, a, b, N=N)
                got = ('K', r[2]) if r[0] == 'K' else (r[0],)
                p = predict(P, ds, a, b)
                kind = kind_of(ds, a, b)
                if a == 1 and not ds:
                    kind = 'R1->R4'
                kh = P['mh'] * b + P['ch']
                if a == 0 and kind in ('R3', 'HALT?', 'R3big') and 0 < trailing_zeros(ds) < len(ds):
                    k = trailing_zeros(ds)
                    kind = 'R3' if k < kh else ('HALT' if k == kh else 'R3big')
                ok = (p is None) or got == p
                stats.setdefault(kind, [0, 0])
                stats[kind][0] += 1
                stats[kind][1] += ok
                if not ok:
                    bad.append((kind, (ds, a, b), got, p))
            print('  grid: ' + ', '.join('%s %d/%d' % (k, v[1], v[0]) for k, v in sorted(stats.items()))
                  + ('  (R3big not predicted)' if 'R3big' in stats else ''))
            for kind, c, got, p in bad[:10]:
                print('    MISMATCH %-6s %s: got %s, predicted %s' % (
                    kind, show(c), show(got[1]) if got[0] == 'K' else got, show(p[1]) if p and p[0] == 'K' else p))


if __name__ == '__main__':
    main()
