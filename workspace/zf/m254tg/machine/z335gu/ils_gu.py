"""ILS for the UREP variants: order, UREP flips / vmap (perm of v0..v5) / Trans variables / param perm.
usage: python ils_gu.py SEED MINUTES DROPINF OUT.json"""
import sys, json, random, itertools, time
import gu, zfp, forms
seed, minutes, drop, out = int(sys.argv[1]), float(sys.argv[2]), sys.argv[3] == '1', sys.argv[4]
rng = random.Random(seed)
base = json.load(open('R3Y1_335.json'))
cfg0 = gu.variant_cfg(base, 'UREP_32', drop_inf=drop)
n = len(cfg0['clauses']); ui = cfg0['clauses'].index('UREP_32')
NF = forms.nflip(forms.TREES['UREP'])
PERMS = list(itertools.permutations((1, 2, 3)))
cache = {}
def cfg_of(st):
    o, fl, vm, tpq, pm = st
    c = json.loads(json.dumps(cfg0))
    nm = 'UREP_%d%d' % tpq
    c['clauses'][ui] = nm; c['order'] = list(o)
    c['perm'].pop('UREP_32', None); c['perm'][nm] = list(pm)
    c['flips'].pop('UREP_32', None)
    if fl: c['flips'][nm] = fl
    if tuple(vm) != tuple(range(6)): c['vmap'][nm] = list(vm)
    return c
def cost(st):
    if st not in cache:
        c = cfg_of(st)
        if not zfp.valid(c['clauses'], c['order'], c['opt']): cache[st] = 10**6
        else:
            try: cache[st] = zfp.count(gu.build(c))
            except (AssertionError, RecursionError): cache[st] = 10**6
    return cache[st]
def neighbors(st):
    o, fl, vm, tpq, pm = st
    for b in range(NF): yield (o, fl ^ (1 << b), vm, tpq, pm)
    for i in range(6):
        for j in range(i + 1, 6):
            v = list(vm); v[i], v[j] = v[j], v[i]; yield (o, fl, tuple(v), tpq, pm)
    for t in gu.TPQ:
        if t != tpq: yield (o, fl, vm, t, pm)
    for q in PERMS:
        if q != pm: yield (o, fl, vm, tpq, q)
    for mid in range(1, n):
        for left in range(mid):
            for right in range(mid + 1, n + 1):
                yield (o[:left] + o[mid:right] + o[left:mid] + o[right:], fl, vm, tpq, pm)
def perturb(st):
    o, fl, vm, tpq, pm = st
    o = list(o)
    for _ in range(rng.randint(1, 3)):
        k = rng.randrange(5)
        if k == 0: fl ^= 1 << rng.randrange(NF)
        elif k == 1:
            v = list(vm); i, j = rng.sample(range(6), 2); v[i], v[j] = v[j], v[i]; vm = tuple(v)
        elif k == 2: tpq = rng.choice(gu.TPQ)
        elif k == 3: pm = rng.choice(PERMS)
        else:
            i, j = rng.sample(range(n), 2); o.insert(j, o.pop(i))
    return (tuple(o), fl, vm, tpq, pm)
def climb(st):
    c = cost(st)
    while True:
        nb = list(neighbors(st)); rng.shuffle(nb)
        for s2 in nb:
            c2 = cost(s2)
            if c2 < c: st, c = s2, c2; break
        else: return st, c
start = (tuple(cfg0['order']), 0, tuple(range(6)), (3, 2), tuple(cfg0['perm']['UREP_32']))
print('start', cost(start), flush=True)
cur, cc = climb(start); best, bc = cur, cc
print('climb', cc, flush=True)
t_end = time.time() + 60 * minutes
while time.time() < t_end:
    s2, c2 = climb(perturb(cur))
    if c2 <= cc: cur, cc = s2, c2
    if c2 < bc:
        best, bc = s2, c2; print('best', bc, '%.0fs' % (time.time() - t_end + 60 * minutes), flush=True)
        json.dump(cfg_of(best), open(out, 'w'), indent=1)
json.dump(cfg_of(best), open(out, 'w'), indent=1)
print('final', bc, 'evals', len(cache), flush=True)
