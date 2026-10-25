"""Iterated local search over (order, perms, [vmaps, flips]) for zfp variants.
Full-neighborhood first-improvement descent, then a random kick of K moves from the best; repeat.
usage: python ils.py SEED OUT.json HOURS OPT(json) INIT.json [K]"""
import sys, json, random, itertools, time
import lowprio, zfp, forms

seed = int(sys.argv[1]); out = sys.argv[2]; hours = float(sys.argv[3])
opt = json.loads(sys.argv[4]); init = json.load(open(sys.argv[5]))
K = int(sys.argv[6]) if len(sys.argv) > 6 else 3
rng = random.Random(seed)
clauses = init['clauses']; n = len(clauses)
PERMS = list(itertools.permutations((1, 2, 3)))
permable = [c for c in clauses if c not in zfp.CLOSED]
VM = 'vmap' in opt
closed = [c for c in clauses if c in zfp.CLOSED or c == 'REP']
NFL = {c: forms.nflip(forms.TREES[c]) for c in closed}
VMAPS = list(itertools.permutations(range(5), 4))
cache = {}

def key(st):
    o, p = st
    return (tuple(o), tuple(sorted((k, tuple(v) if isinstance(v, list) else v) for k, v in p.items())))

def split(p):
    return ({k: v for k, v in p.items() if ':' not in k},
            {k[3:]: v for k, v in p.items() if k.startswith('vm:')},
            {k[3:]: v for k, v in p.items() if k.startswith('fl:')})

def cost(st):
    k = key(st)
    if k not in cache:
        o, p = st
        if not zfp.valid(clauses, o, opt): cache[k] = 10**6
        else:
            pp, vm, fl = split(p)
            cache[k] = zfp.cost(zfp.make(clauses, pp, opt, vm, fl), o)
    return cache[k]

def neighbors(st):
    o, p = st
    for mid in range(1, n):
        for left in range(mid):
            for right in range(mid + 1, n + 1):
                yield (o[:left] + o[mid:right] + o[left:mid] + o[right:], p)
    for c in permable:
        for q in PERMS:
            if q != tuple(p.get(c, zfp.ID)):
                p2 = dict(p); p2[c] = q
                if q == zfp.ID: del p2[c]
                yield (o, p2)
    if VM:
        for c in closed:
            for b in range(NFL[c]):
                p2 = dict(p); p2['fl:' + c] = p.get('fl:' + c, 0) ^ (1 << b)
                if p2['fl:' + c] == 0: del p2['fl:' + c]
                yield (o, p2)
            if c == 'REP': continue      # no renaming inside the REP scheme (capture subtleties)
            for m in rng.sample(VMAPS, 12):
                p2 = dict(p); p2['vm:' + c] = m
                if m == (0, 1, 2, 3): del p2['vm:' + c]
                yield (o, p2)

def kick(st):
    o, p = list(st[0]), dict(st[1])
    for _ in range(K):
        r = rng.random()
        if r < 0.5:
            i, j = sorted(rng.sample(range(n + 1), 2)); blk = o[i:j]; rest = o[:i] + o[j:]
            k = rng.randrange(len(rest) + 1); o = rest[:k] + blk + rest[k:]
        elif r < 0.8 or not VM:
            c = rng.choice(permable); p[c] = rng.choice(PERMS)
        else:
            c = rng.choice(closed); p['fl:' + c] = rng.randrange(1 << NFL[c]) if NFL[c] else 0
            if not p['fl:' + c]: del p['fl:' + c]
    return (o, p)

def dump(v, st):
    pp, vm, fl = split(st[1])
    json.dump({'count': v, 'order': st[0], 'clauses': clauses, 'opt': opt, 'perm': pp,
               'vmap': vm, 'flips': fl}, open(out, 'w'))

p0 = {k: tuple(v) for k, v in init.get('perm', {}).items()}
p0.update({'vm:' + k: tuple(v) for k, v in init.get('vmap', {}).items()})
p0.update({'fl:' + k: v for k, v in init.get('flips', {}).items()})
best = (init['order'], p0); bv = cost(best)
print('start', bv, flush=True)
t0 = time.time(); cur = best; cv = bv
while time.time() - t0 < hours * 3600:
    improved = True
    while improved:
        improved = False
        nb = list(neighbors(cur)); rng.shuffle(nb)
        for st in nb:
            v = cost(st)
            if v < cv:
                cur, cv, improved = st, v, True
                break
    if cv <= bv:
        if cv < bv: print(f'{cv} t={time.time()-t0:.0f}s', flush=True)
        best, bv = cur, cv; dump(bv, best)
    cur = kick(best); cv = cost(cur)
print('final', bv, flush=True)
dump(bv, best)
