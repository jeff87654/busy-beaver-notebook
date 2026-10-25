"""Joint hill-climb over clause order + per-clause parameter permutations (zfp).
usage: python climbp.py SEED OUT.json [ITERS] [clauses-json|-] [opt-json|-] [init.json]"""
import sys, json, random, itertools
import lowprio, zfp
seed = int(sys.argv[1]); out = sys.argv[2]
iters = int(sys.argv[3]) if len(sys.argv) > 3 else 10**9
clauses = zfp.BASE if len(sys.argv) <= 4 or sys.argv[4] == '-' else json.loads(sys.argv[4])
opt = [] if len(sys.argv) <= 5 or sys.argv[5] == '-' else json.loads(sys.argv[5])
rng = random.Random(seed)
n = len(clauses)
PERMS = list(itertools.permutations((1, 2, 3)))
permable = [c for c in clauses if c not in ('EXT', 'POW', 'UNI', 'INF')]
forbid = {i for i, c in enumerate(clauses) if c in zfp.PREMISE}
if len(sys.argv) > 6:
    init = json.load(open(sys.argv[6])); order = init['order']; perm = {k: tuple(v) for k, v in init['perm'].items()}
else:
    order = list(range(n)); perm = {}
    if seed:
        rng.shuffle(order)
        perm = {c: rng.choice(PERMS) for c in permable}
while not zfp.valid(clauses, order, opt): rng.shuffle(order)
def cost(o, p): return zfp.cost(zfp.make(clauses, p, opt), o)
best = cost(order, perm); print('start', best, flush=True)
def moves(order, perm):
    for mid in range(1, n):
        for left in range(mid):
            for right in range(mid + 1, n + 1):
                yield ('o', order[:left] + order[mid:right] + order[left:mid] + order[right:])
    for c in permable:
        for p in PERMS:
            if p != perm.get(c, zfp.ID): yield ('p', (c, p))
it = 0; changed = True
while changed and it < iters:
    changed = False
    ms = list(moves(order, perm)); rng.shuffle(ms)
    for kind, m in ms:
        if kind == 'o':
            if not zfp.valid(clauses, m, opt): continue
            o2, p2 = m, perm
        else:
            o2, p2 = order, dict(perm); p2[m[0]] = m[1]
        v = cost(o2, p2); it += 1
        if v < best or (v == best and rng.random() < 0.02):
            if v < best: changed = True
            best, order, perm = v, o2, p2
            print(best, kind, m if kind == 'p' else '', flush=True)
            json.dump({'count': best, 'order': order, 'perm': perm, 'clauses': clauses, 'opt': opt}, open(out, 'w'))
            if v < best or changed: break
print('final', best, order, perm, flush=True)
json.dump({'count': best, 'order': order, 'perm': perm, 'clauses': clauses, 'opt': opt}, open(out, 'w'))
