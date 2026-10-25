"""Late-acceptance hill climbing over (clause order, per-clause parameter permutation) for zfp variants.
usage: python anneal.py SEED OUT.json EVALS CLAUSES(json|-) OPT(json|-) [INIT.json] [LA_LEN]
Writes the best configuration found to OUT.json whenever it improves."""
import sys, json, random, itertools, time
import lowprio, zfp

seed = int(sys.argv[1]); out = sys.argv[2]; evals = int(sys.argv[3])
clauses = zfp.BASE if sys.argv[4] == '-' else json.loads(sys.argv[4])
opt = [] if sys.argv[5] == '-' else json.loads(sys.argv[5])
init = json.load(open(sys.argv[6])) if len(sys.argv) > 6 and sys.argv[6] != '-' else None
LA = int(sys.argv[7]) if len(sys.argv) > 7 else 50
rng = random.Random(seed)
n = len(clauses)
PERMS = list(itertools.permutations((1, 2, 3)))
permable = [c for c in clauses if c not in zfp.CLOSED]
cache = {}

VM = 'vmap' in opt     # Track B: allow renaming variables in the closed ZF axioms
VMAPS = [m for m in itertools.permutations(range(5), 4)]
closed = [c for c in clauses if c in zfp.CLOSED or c == 'REP']

import forms
NFL = {c: forms.nflip(forms.TREES[c]) for c in closed}

def split(p):
    return ({k: v for k, v in p.items() if ':' not in k},
            {k[3:]: v for k, v in p.items() if k.startswith('vm:')},
            {k[3:]: v for k, v in p.items() if k.startswith('fl:')})

def cost(o, p):
    key = (tuple(o), tuple(sorted(p.items())))
    if key not in cache:
        pp, vm, fl = split(p)
        cache[key] = zfp.cost(zfp.make(clauses, pp, opt, vm, fl), o)
    return cache[key]

if init and init.get('clauses') == clauses:
    order = list(init['order']); perm = {k: tuple(v) for k, v in init.get('perm', {}).items()}
    perm.update({'vm:' + k: tuple(v) for k, v in init.get('vmap', {}).items()})
    perm.update({'fl:' + k: v for k, v in init.get('flips', {}).items()})
else:
    order = list(range(n)); perm = {}
    rng.shuffle(order)
while not zfp.valid(clauses, order, opt):
    rng.shuffle(order)

def neighbor(o, p):
    r = rng.random()
    o = list(o); p = dict(p)
    if r < 0.35:      # block move
        i, j = sorted(rng.sample(range(n + 1), 2))
        blk = o[i:j]; rest = o[:i] + o[j:]
        k = rng.randrange(len(rest) + 1)
        o = rest[:k] + blk + rest[k:]
    elif r < 0.6:     # swap
        i, j = rng.sample(range(n), 2); o[i], o[j] = o[j], o[i]
    elif r < 0.75:    # single move
        i = rng.randrange(n); x = o.pop(i); o.insert(rng.randrange(n), x)
    elif VM and r < 0.82:   # variable renaming of a closed axiom
        c = rng.choice(closed); p['vm:' + c] = rng.choice(VMAPS)
        if p['vm:' + c] == (0, 1, 2, 3): del p['vm:' + c]
    elif VM and r < 0.9:    # operand swap in a closed axiom
        c = rng.choice([c for c in closed if NFL[c]])
        p['fl:' + c] = p.get('fl:' + c, 0) ^ (1 << rng.randrange(NFL[c]))
        if p['fl:' + c] == 0: del p['fl:' + c]
    else:             # permutation change
        c = rng.choice(permable); p[c] = rng.choice(PERMS)
        if p[c] == zfp.ID: del p[c]
    return o, p

def dump(best, bo, bp):
    pp, vm, fl = split(bp)
    json.dump({'count': best, 'order': bo, 'clauses': clauses, 'opt': opt,
               'perm': pp, 'vmap': vm, 'flips': fl}, open(out, 'w'))

cur = cost(order, perm); best = cur; bo, bp = order, perm
hist = [cur] * LA
t0 = time.time()
for it in range(evals):
    o2, p2 = neighbor(order, perm)
    if not zfp.valid(clauses, o2, opt):
        continue
    v = cost(o2, p2)
    if v <= cur or v <= hist[it % LA]:
        order, perm, cur = o2, p2, v
    hist[it % LA] = cur
    if cur < best:
        best, bo, bp = cur, order, perm
        print(f'{best} it={it} t={time.time()-t0:.0f}s', flush=True)
        dump(best, bo, bp)
print('final', best, bo, bp, flush=True)
dump(best, bo, bp)
