"""regime.py -- test oracle-inferred forms (oracle_cache.pkl) across magnitude regimes:
huge tokens and the accumulator get representatives that are small (10..30) or large (300..3000), in all
combinations (respecting residues), and the fitted affine form must reproduce the literal event."""
import pickle, itertools, random, sys
from lib import word, tokens, run, M10, bforms, ctok
cache = pickle.load(open('oracle_cache.pkl', 'rb'))
rnd = random.Random(7)
def rep_val(kind, r, regime):
    if regime == 'S':
        base = rnd.randint(4, 10)
    else:
        base = rnd.randint(100, 1000)
    m = 6 if kind == 'y' else 3
    return r % m + m * base
bad_shapes = []
for shape, form in cache.items():
    if isinstance(form, str):
        continue
    hpos = [i for i, v in enumerate(shape) if isinstance(v, tuple)]
    fails = []
    for regimes in itertools.product('SL', repeat=len(hpos)):
        for trial in range(2):
            rep = list(shape)
            for p, rg in zip(hpos, regimes):
                kind = 'y' if p == len(shape) - 1 else 't'
                rep[p] = rep_val(kind, shape[p][1], rg)
            out = []
            for f in form:
                if f[0] == 'c': out.append(f[1])
                elif f[0] == 'h': out.append(rep[f[1]] + f[2])
                else: out.append(2 * rep[f[1]] + f[2])
            snaps, end = run(M10, word(rep), 'G', '0', 3 * 10**7, ['snap=G0', 'bform', 'maxsnap=2'])
            got = None; beyond = None
            for s in snaps:
                if s[0] == 0: continue
                got = tokens(s[1]); beyond = s[4] < -len(word(rep)); break
            if beyond:
                continue  # needs left context in this representation; skip
            if got != out:
                fails.append((''.join(regimes), rep, got))
    status = 'OK' if not fails else 'FAIL %d' % len(fails)
    print(status, shape, '->', form)
    for f in fails[:3]:
        print('     regime', f[0], 'rep', f[1], 'got', f[2])
    if fails: bad_shapes.append(shape)
print('shapes with magnitude dependence:', len(bad_shapes))
