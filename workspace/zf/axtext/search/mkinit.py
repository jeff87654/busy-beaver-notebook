"""Derive an initial search config from a base config by substituting / removing clauses.
usage: python mkinit.py BASE.json OUT.json [OLD=NEW ...] [-DROP ...]"""
import sys, json, forms
base = json.load(open(sys.argv[1])); out = sys.argv[2]
sub = dict(a.split('=') for a in sys.argv[3:] if '=' in a)
drop = {a[1:] for a in sys.argv[3:] if a.startswith('-')}
cl = base['clauses']
keep = [i for i, c in enumerate(cl) if c not in drop]
newidx = {i: k for k, i in enumerate(keep)}
clauses = [sub.get(cl[i], cl[i]) for i in keep]
order = [newidx[i] for i in base['order'] if i in newidx]
perm = {sub.get(k, k): v for k, v in base.get('perm', {}).items() if k not in drop}
vmap = {sub.get(k, k): v for k, v in base.get('vmap', {}).items() if k not in drop and k not in sub}
flips = {}
for k, v in base.get('flips', {}).items():
    if k in drop: continue
    n = sub.get(k, k)
    flips[n] = v & ((1 << forms.nflip(forms.TREES[n])) - 1)
json.dump({'clauses': clauses, 'order': order, 'perm': perm, 'opt': base['opt'], 'vmap': vmap, 'flips': flips},
          open(out, 'w'), indent=1)
import zfp
p = {k: tuple(v) for k, v in perm.items()}
print(out, zfp.cost(zfp.make(clauses, p, base['opt'], vmap, flips), order), 'valid', zfp.valid(clauses, order, base['opt']))
