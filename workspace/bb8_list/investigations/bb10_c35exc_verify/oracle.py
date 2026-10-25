"""oracle.py -- infer one B-form event of a token list (with huge tokens) from literal runs of sim.exe.

Huge tokens are replaced by representatives (same residue mod 3; the accumulator y also mod 6), the
literal machine is run to the next B-form event, and every output token is fitted as an affine form
(constant, rep+c, 2*rep+c).  The fit must be exact on all samples.  If any sample reads a cell left of
the list, the event needs left context (rules.Need).
"""
import itertools, random
from lib import word, tokens, run, M10
from num import H, add, dbl_add, is_huge, res
import rules

cache = {}
NSAMP = 10
stats = {'calls': 0, 'cached': 0}


def shape_key(t):
    out = []
    for idx, v in enumerate(t):
        if is_huge(v):
            out.append(('H', res(v, 6) if idx == len(t) - 1 else res(v, 3)))
        else:
            out.append(v)
    return tuple(out)


def literal_next(toks, maxsteps=5 * 10**6):
    w = word(toks)
    snaps, end = run(M10, w, 'G', '0', maxsteps, ['snap=G0', 'bform', 'maxsnap=2'])
    for s in snaps:
        if s[0] == 0:
            continue
        beyond = s[4] < -len(w)
        return tokens(s[1]), beyond
    return None, None


def oracle_event(t):
    t = list(t)
    stats['calls'] += 1
    hpos = [i for i, v in enumerate(t) if is_huge(v)]
    key = shape_key(t)
    if key in cache:
        stats['cached'] += 1
        form = cache[key]
    else:
        form = infer(t, hpos)
        cache[key] = form
    if form == 'NEED':
        raise rules.Need('oracle: reads left of list')
    if isinstance(form, str):
        raise rules.Unknown(form)
    # build output
    out = []
    for f in form:
        kind = f[0]
        if kind == 'c':
            out.append(f[1])
        elif kind == 'h':      # rep_p + c
            out.append(add(t[f[1]], f[2]))
        elif kind == 'h2':     # 2*rep_p + c
            out.append(dbl_add(t[f[1]], f[2]))
    lo = 0
    while lo < len(t) and lo < len(out) and t[lo] == out[lo]:
        lo += 1
    return rules.Event('ORC', lo, out)


def infer(t, hpos):
    rnd = random.Random(12345 + len(t))
    samples = []
    for sidx in range(NSAMP):
        rep = list(t)
        vals = {}
        for p in hpos:
            if p == len(t) - 1:
                r6 = res(t[p], 6)
                v = r6 + 6 * rnd.randint(4, 12)
            else:
                r3 = res(t[p], 3)
                v = r3 + 3 * rnd.randint(10, 22)
            rep[p] = v
            vals[p] = v
        if any(not isinstance(v, int) for v in rep):
            return 'oracle: non-int'
        nxt, beyond = literal_next(rep)
        if nxt is None:
            return 'oracle: no B-form event (runaway?) for shape %s' % (shape_key(t),)
        if beyond:
            return 'NEED'
        if any(not isinstance(v, int) for v in nxt):
            return 'oracle: unparsable output'
        samples.append((vals, nxt))
    L = len(samples[0][1])
    if any(len(s[1]) != L for s in samples):
        return 'oracle: output length varies with huge values'
    form = []
    for pos in range(L):
        outs = [s[1][pos] for s in samples]
        if all(o == outs[0] for o in outs):
            form.append(('c', outs[0])); continue
        found = None
        for p in hpos:
            for mul in (1, 2):
                cs = set(o - mul * s[0][p] for o, s in zip(outs, samples))
                if len(cs) == 1:
                    found = ('h' if mul == 1 else 'h2', p, cs.pop()); break
            if found:
                break
        if not found:
            return 'oracle: no affine fit at output position %d' % pos
        form.append(found)
    return form
