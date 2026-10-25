"""Parameterized literal rule verifier for K-family variants of the digit-list counter.

    python kcheck.py TM [--show KIND] [--json out.json] [--maxb B]

1. Fits the blank reset R4 from literal runs K(;0;b), b = 1..6, to the form
       K(; 0; b) -> K(P + 1^(4b+c); a0; b0)        (P a fixed top-digit prefix; c, a0, b0 constants)
   and reports it (or reports the raw successors if they do not fit).
2. Runs the standard grid (kfam.grid: up to 3 digits 0-3, a = 0-3, b = 1-5, zero blocks k = 1..4b+4)
   literally until the next K configuration, and compares each result with the parent's rules R1-R3
   (+ fitted R4, + halt at k = 4b+1, + the parent's k >= 4b+2 form, with its END4 tail replaced by the fitted one).
3. Prints per-kind match counts and the first mismatches.  `--show KIND` lists every observation of that kind
   (R1, R2, R3, R3big, HALT?, R4), which is the quickest way to read off a changed rule.
"""
import sys
import json
from kfam import run_next, parent_predict, kind_of, grid, show, trailing_zeros, strip


def fit_r4(tm, bs=range(1, 7)):
    obs = {}
    for b in bs:
        obs[b] = run_next(tm, (), 0, b, N=10 ** 7)
    ok = all(o[0] == 'K' for o in obs.values())
    if not ok:
        return None, obs
    fits = []
    for b, o in obs.items():
        ds, a0, b0 = o[2]
        n = 0
        while n < len(ds) and ds[len(ds) - 1 - n] == 1:
            n += 1
        fits.append((tuple(ds[:len(ds) - n]), n - 4 * b, a0, b0))
    # allow the prefix to absorb trailing 1s consistently: take the fit with constant (P, c, a0, b0)
    if len(set(fits)) == 1:
        P, c, a0, b0 = fits[0]
        return (lambda b, P=P, c=c, a0=a0, b0=b0: (strip(P + (1,) * (4 * b + c)), a0, b0)), dict(P=P, c=c, a=a0, b=b0)
    return None, obs


def predict(ds, a, b, r4):
    p = parent_predict(ds, a, b, r4)
    if p is not None:
        return p
    # k >= 4b+2: parent form ds[:i+1] (y+1 kept) + 0^(k-4b-2) + (END4 tail); tail = r4(b') digits with 4b ones
    k = trailing_zeros(ds)
    i = len(ds) - 1 - k
    tail, a0, b0 = r4(b)
    return ('K', (strip(tuple(ds[:i + 1]) + (0,) * (k - 4 * b - 2) + tail), a0, b0))


def main():
    tm = sys.argv[1]
    show_kind = sys.argv[sys.argv.index('--show') + 1] if '--show' in sys.argv else None
    out_json = sys.argv[sys.argv.index('--json') + 1] if '--json' in sys.argv else None
    maxb = int(sys.argv[sys.argv.index('--maxb') + 1]) if '--maxb' in sys.argv else 5
    r4, info = fit_r4(tm)
    print('machine', tm)
    if r4 is None:
        print('R4 does not fit P + 1^(4b+c):')
        for b, o in info.items():
            print('   K(;0;%d) ->' % b, show(o[2]) if o[0] == 'K' else o[:3])
        r4 = lambda b: None
    else:
        print('R4 fit: K(;0;b) -> K(%s 1^(4b%+d); %d; %d)' % (
            ''.join('%d,' % d for d in info['P']), info['c'], info['a'], info['b']))
    stats = {}
    bad = []
    rec = []
    for ds, a, b in grid(maxb=maxb):
        r = run_next(tm, ds, a, b, N=10 ** 7)
        got = ('K', r[2]) if r[0] == 'K' else (r[0],) + ((r[2],) if r[0] == 'HALT' else ())
        try:
            p = predict(ds, a, b, r4)
        except TypeError:
            p = None
        gotc = got if got[0] != 'HALT' else ('HALT',)
        ok = (gotc == p)
        kind = kind_of(ds, a, b)
        if a == 1 and not ds:
            kind = 'R1->R4'
        stats.setdefault(kind, [0, 0])
        stats[kind][0] += 1
        stats[kind][1] += ok
        rec.append(dict(ds=ds, a=a, b=b, kind=kind, got=str(got), steps=r[1], ok=ok))
        if not ok:
            bad.append((kind, (ds, a, b), got, p))
        if show_kind and kind == show_kind:
            print('  %-8s %-28s -> %-40s %s' % (kind, show((ds, a, b)),
                                                 show(got[1]) if got[0] == 'K' else str(got), 'ok' if ok else 'DIFF'))
    tot = sum(v[0] for v in stats.values())
    good = sum(v[1] for v in stats.values())
    print('cases %d, match %d' % (tot, good))
    for k, (n, ok) in sorted(stats.items()):
        print('  %-8s %4d/%4d match' % (k, ok, n))
    for kind, c, got, p in bad[:25]:
        print('  MISMATCH %-6s %s: got %s, parent-predicted %s' % (
            kind, show(c), show(got[1]) if got[0] == 'K' else got, show(p[1]) if p and p[0] == 'K' else p))
    if out_json:
        json.dump(rec, open(out_json, 'w'))


if __name__ == '__main__':
    main()
