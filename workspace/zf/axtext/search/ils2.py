"""ILS over (order, perms, flips, vmaps, axiom-text variant per family).
usage: python ils2.py SEED OUT.json HOURS INIT.json [K]"""
import sys, json, random, itertools, time
import lowprio, zfp, forms
FAMILIES = [
    ['REPsb0', 'REPsb3', 'REPsb4', 'REPbs0', 'REPbs3', 'REPbs4', 'REPq0', 'REPq3', 'REPq4', 'REPr0', 'REPr3', 'REPr4'],
    ['EXT', 'EXTs'],
    ['INF', 'INF2'],
]
FAM = {n: f for f in FAMILIES for n in f}
seed = int(sys.argv[1]); out = sys.argv[2]; hours = float(sys.argv[3]); init = json.load(open(sys.argv[4]))
K = int(sys.argv[5]) if len(sys.argv) > 5 else 3
rng = random.Random(seed)
opt = init['opt']; n = len(init['clauses'])
PERMS = list(itertools.permutations((1, 2, 3)))
VMAPS = list(itertools.permutations(range(5), 4))
cache = {}
def norm(st):
    names, o, p, vm, fl = st
    return (tuple(names), tuple(o), tuple(sorted((k, tuple(v)) for k, v in p.items())),
            tuple(sorted((k, tuple(v)) for k, v in vm.items())), tuple(sorted(fl.items())))
def cost(st):
    k = norm(st)
    if k not in cache:
        names, o, p, vm, fl = st
        if not zfp.valid(names, o, opt): cache[k] = 10**6
        else: cache[k] = zfp.cost(zfp.make(names, p, opt, vm, fl), o)
    return cache[k]
def closedlike(c): return c in zfp.CLOSED or c in zfp.REPLIKE
def neighbors(st):
    names, o, p, vm, fl = st
    for mid in range(1, n):
        for left in range(mid):
            for right in range(mid + 1, n + 1):
                yield (names, o[:left] + o[mid:right] + o[left:mid] + o[right:], p, vm, fl)
    for c in names:
        if c in zfp.CLOSED: continue
        for q in PERMS:
            if q != tuple(p.get(c, zfp.ID)):
                p2 = dict(p); p2[c] = q
                yield (names, o, p2, vm, fl)
    for c in names:
        if not closedlike(c): continue
        for b in range(forms.nflip(forms.TREES[c])):
            f2 = dict(fl); f2[c] = fl.get(c, 0) ^ (1 << b)
            if not f2[c]: del f2[c]
            yield (names, o, p, vm, f2)
        if c in zfp.REPLIKE: continue
        for m in rng.sample(VMAPS, 12):
            v2 = dict(vm); v2[c] = m
            yield (names, o, p, v2, fl)
    for i, c in enumerate(names):
        for alt in FAM.get(c, []):
            if alt == c: continue
            yield switch(st, i, alt)
def switch(st, i, alt):
    names, o, p, vm, fl = st
    c = names[i]; names2 = list(names); names2[i] = alt
    p2 = dict(p); vm2 = dict(vm); fl2 = dict(fl)
    if c in p2: p2[alt] = p2.pop(c)
    vm2.pop(c, None); f = fl2.pop(c, 0)
    f &= (1 << forms.nflip(forms.TREES[alt])) - 1
    if f: fl2[alt] = f
    return (tuple(names2), o, p2, vm2, fl2)
def kick(st):
    names, o, p, vm, fl = st; o = list(o); p = dict(p); fl = dict(fl)
    for _ in range(K):
        r = rng.random()
        if r < 0.45:
            i, j = sorted(rng.sample(range(n + 1), 2)); blk = o[i:j]; rest = o[:i] + o[j:]
            k = rng.randrange(len(rest) + 1); o = rest[:k] + blk + rest[k:]
        elif r < 0.7:
            c = rng.choice([c for c in names if c not in zfp.CLOSED]); p[c] = rng.choice(PERMS)
        elif r < 0.9:
            c = rng.choice([c for c in names if closedlike(c)]); nf = forms.nflip(forms.TREES[c])
            fl[c] = rng.randrange(1 << nf) if nf else 0
            if not fl[c]: del fl[c]
        else:
            i = rng.choice([i for i, c in enumerate(names) if c in FAM])
            st2 = switch((names, o, p, vm, fl), i, rng.choice(FAM[names[i]]))
            names, o, p, vm, fl = st2; o = list(o); p = dict(p); fl = dict(fl)
    return (names, o, p, vm, fl)
def dump(v, st):
    names, o, p, vm, fl = st
    json.dump({'count': v, 'order': list(o), 'clauses': list(names), 'opt': opt, 'perm': {k: list(x) for k, x in p.items()},
               'vmap': {k: list(x) for k, x in vm.items()}, 'flips': fl}, open(out, 'w'))
best = (tuple(init['clauses']), list(init['order']), {k: tuple(v) for k, v in init.get('perm', {}).items()},
        {k: tuple(v) for k, v in init.get('vmap', {}).items()}, dict(init.get('flips', {})))
bv = cost(best); print('start', bv, flush=True)
t0 = time.time(); cur, cv = best, bv
while time.time() - t0 < hours * 3600:
    improved = True
    while improved:
        improved = False
        nb = list(neighbors(cur)); rng.shuffle(nb)
        for s2 in nb:
            v = cost(s2)
            if v < cv:
                cur, cv, improved = s2, v, True; break
    if cv <= bv:
        if cv < bv: print(f'{cv} t={time.time()-t0:.0f}s {cur[0]}', flush=True)
        best, bv = cur, cv; dump(bv, best)
    cur = kick(best); cv = cost(cur)
print('final', bv, flush=True); dump(bv, best)
