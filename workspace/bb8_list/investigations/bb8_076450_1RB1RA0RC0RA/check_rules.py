"""Exact literal checks of the family rules (no acceleration).
K(ds; a; b) = 0^inf 1^d1 0 ... 0 1^dn 0 1^a 0 1^b 0 1 B>0 0^inf (ds top digit first, as printed).
Predicted successor (first later configuration of the same shape):
  a >= 1                         : K(ds; a-1; 4b+4)                                   (R1)
  a = 0, last digit x+1          : K(..., x; 4b+3; 1)                                 (R2)
  a = 0, k >= 1 trailing zeros,
     k <= 4b                     : K(..., y, 4b+3-k, 1^(k-1); 1; 1)                   (R3)
     k = 4b+1                    : HALT                                               (never reached)
     k >= 4b+2 (nonzero digit left): K(..., y+1, 0^(k-4b-2), 2, 1^(4b); 1; 1)         (never reached)
  a = 0, no digits (blank)       : variant-specific R4 result, e.g. main K(2, 1^(4b); 1; 1)
Usage: python check_rules.py [TM]  -> prints summary; writes check_rules.json"""
import sys, json, itertools
from kfam import run_next
from lit import MAIN
P = '1RB1RA_0RC0RA_0LD1RC_1RE1LE_1LF0LG_1LB0RD_'
R4 = {  # blank reset: b -> (ds, a, b)
    '0LH1LF_1RF---': lambda b: ((2,) + (1,) * (4 * b), 1, 1),
    '1LH1LF_0RA---': lambda b: ((2,) + (1,) * (4 * b), 1, 1),
    '1LH1LF_1LA---': lambda b: ((1, 2) + (1,) * (4 * b), 1, 1),
    '1LH1LF_1RA---': lambda b: ((3,) + (1,) * (4 * b), 1, 1),
    '1LH1LF_1RB---': lambda b: ((1,) * (4 * b + 2), 1, 1),
    '1LH1LF_0RB---': lambda b: ((1,) * (4 * b + 1), 1, 1),
    '0LH1LF_1LA---': lambda b: ((5,) + (1,) * (4 * b - 1), 1, 1),
}
def predict(ds, a, b, v):
    ds = list(ds)
    if a >= 1:
        if not ds and a == 1:  # K((),0,4b+4) is not a parseable shape: next one is after R4
            return ('K', R4[v](4 * b + 4))
        return ('K', (tuple(ds), a - 1, 4 * b + 4))
    k = 0
    while k < len(ds) and ds[len(ds) - 1 - k] == 0: k += 1
    if k == len(ds):
        return ('K', R4[v](b))
    i = len(ds) - 1 - k
    if k == 0:
        ds[-1] -= 1; out = (ds, 4 * b + 3, 1)
    elif k <= 4 * b:
        ds[i] -= 1; ds = ds[:i + 1] + [4 * b + 3 - k] + [1] * (k - 1); out = (ds, 1, 1)
    elif k == 4 * b + 1:
        return ('HALT',)
    elif v in ('0LH1LF_1RF---', '1LH1LF_0RA---'):
        ds = ds[:i + 1] + [0] * (k - 4 * b - 2) + [2] + [1] * (4 * b); out = (ds, 1, 1)
    else:
        return None  # uses END4 with a non-blank left part: variant-specific, unreachable, not predicted
    ds, a2, b2 = out
    while ds and ds[0] == 0: ds = ds[1:]
    return ('K', (tuple(ds), a2, b2))
def main():
    v = sys.argv[1] if len(sys.argv) > 1 else MAIN[len(P):]
    tm = P + v
    cases = []
    for n in range(0, 4):
        for ds in itertools.product(range(0, 4), repeat=n):
            if ds and ds[0] == 0: continue
            for a in range(0, 4):
                for b in range(1, 6):
                    cases.append((ds, a, b))
    # long zero blocks (R3 up to and beyond the halting boundary k = 4b+1)
    for b in range(1, 4):
        for k in range(1, 4 * b + 5):
            for y in (1, 2):
                cases.append(((1, y) + (0,) * k, 0, b))
    stats = {}; bad = []; rec = []
    for ds, a, b in cases:
        r = run_next(ds, a, b, N=10 ** 7, tm=tm)
        p = predict(ds, a, b, v)
        got = ('K', r[2]) if r[0] == 'K' else (r[0],)
        ok = got == p if p is not None else True
        kind = 'R1' if a >= 1 else 'reset'
        if a == 0:
            kz = 0
            while kz < len(ds) and ds[len(ds) - 1 - kz] == 0: kz += 1
            kind = 'R4' if kz == len(ds) else ('R2' if kz == 0 else ('R3' if kz <= 4 * b else ('HALT' if kz == 4 * b + 1 else 'R4like')))
        if p is None: kind = 'R4like(not predicted)'
        stats.setdefault(kind, [0, 0]); stats[kind][0] += 1; stats[kind][1] += ok
        rec.append(dict(ds=ds, a=a, b=b, kind=kind, got=str(got), steps=r[1], ok=ok))
        if not ok: bad.append((ds, a, b, got, p))
    print('variant', v, 'cases', len(cases))
    for k, (n, ok) in sorted(stats.items()):
        print('  %-22s %4d/%4d match' % (k, ok, n))
    for x in bad[:20]: print('  MISMATCH', x)
    json.dump(rec, open('check_rules_%s.json' % v.replace('---', ''), 'w'))
main()
