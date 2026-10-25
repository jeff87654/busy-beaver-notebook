"""Coordinate descent over closed-axiom variable renamings (and flips) for a fixed order/perm."""
import sys, json, itertools, zfp, forms
import lowprio
cfg = json.load(open(sys.argv[1])); out = sys.argv[2]
perm = {k: tuple(v) for k, v in cfg['perm'].items()}
vm = {k: tuple(v) for k, v in cfg.get('vmap', {}).items()}; fl = dict(cfg.get('flips', {}))
cl = cfg['clauses']; opt = cfg['opt']
def cost(): return zfp.cost(zfp.make(cl, perm, opt, vm, fl), cfg['order'])
best = cost(); print('start', best, flush=True)
closed = [c for c in cl if c in forms.TREES]
REPFLIPONLY = True
improved = True
while improved:
    improved = False
    for c in closed:
        for m in ([(0, 1, 2, 3)] if c == 'REP' else itertools.permutations(range(5), 4)):
            for f in range(1 << forms.nflip(forms.TREES[c])):
                old = (vm.get(c), fl.get(c))
                vm[c] = m; fl[c] = f
                v = cost()
                if v < best:
                    best = v; improved = True; print(best, c, m, f, flush=True)
                    cfg.update(count=best, vmap=vm, flips=fl); json.dump(cfg, open(out, 'w'))
                else:
                    if old[0] is None: vm.pop(c)
                    else: vm[c] = old[0]
                    if old[1] is None: fl.pop(c)
                    else: fl[c] = old[1]
print('final', best, flush=True)
