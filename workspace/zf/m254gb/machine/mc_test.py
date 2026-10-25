"""Small-model truth tables for family-E/F components (labelled formulas).
usage: python mc_test.py <module> <builder> [k=v ...] [lab=<json>]"""
import sys, json, importlib
from ngdsl import greedy_labels, check
from modelcheck import *
mod = importlib.import_module(sys.argv[1]); build = getattr(mod, sys.argv[2])
o = dict(mod.DEFAULT); lab = None
for a in sys.argv[3:]:
    if a.startswith('lab='): lab = json.loads(a[4:]); continue
    if a.startswith('o='): o.update(json.loads(a[2:])); continue
    k, v = a.split('='); o[k] = int(v)
f = build(o)
if lab is None: lab = greedy_labels(f)
assert check(f, lab)
L = lambda g: relabel(g, lab)
ln = lab['n']
expect = {'small': [1,1,0,0], 'comp': [1,0,0,0], 'ev': [0,0,0,0], 'gf': [0,1,0,0]}
ok = True
KMAX = 4
for name in ['small', 'comp', 'ev', 'gf']:
    g = getattr(mod, name)(o)
    row = [int(ev(L(g), {ln: ordinal(k)}, universe(ordinal(k)))) for k in range(KMAX)]
    exp = expect[name]
    if name == 'gf' and not o.get('tw0', 0) and sys.argv[1] in ('cands5',): exp = [1,1,0,0]
    print(name, row, "expected", exp, flush=True)
# whole sentence body psi(n) on every n of size <= 3 drawn from V_4 (must be false: GC holds below 4)
V = [frozenset()]
for _ in range(3): V = powerset(V)
V4 = powerset(V)
psi = L(f[2])
bad = [n for n in V4 if len(n) <= 2 and ev(psi, {ln: n}, universe(n))]
print('psi(n) true for', len(bad), 'sets n in V_4 with |n|<=2 (must be 0)')
