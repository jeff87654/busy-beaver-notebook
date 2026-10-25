"""Small-model checks of the chosen NG' (chosen.json): component truth tables on ordinals 0..3,
and psi(n) false for every n in V_4 with |n| <= 2."""
import json, importlib
from ngdsl import check
from modelcheck import *
import ng_final
f, lab, c = ng_final.chosen()
mod = importlib.import_module(c['module']); o = dict(mod.DEFAULT); o.update(c['o'])
L = lambda g: relabel(g, lab); ln = lab['n']
gf0 = 0 if o.get('tw0') else 1
expect = {'small': [1,1,0,0], 'comp': [1,0,0,0], 'ev': [o.get('tw0',0),0,0,0], 'gf': [1-gf0 if False else (0 if o.get('tw0') else 1),1,0,0]}
allok = True
for name in ['small', 'comp', 'ev', 'gf']:
    g = getattr(mod, name)(o)
    row = [int(ev(L(g), {ln: ordinal(k)}, universe(ordinal(k)))) for k in range(4)]
    ok = row == expect[name]; allok &= ok
    print(f'{name:5s} n=0..3: {row}  expected {expect[name]}  {"OK" if ok else "MISMATCH"}', flush=True)
V = [frozenset()]
for _ in range(3): V = powerset(V)
V5 = powerset(V)                # V_5 (V is V_4)
psi = L(f[2])
bad = [n for n in V5 if len(n) <= 2 and ev(psi, {ln: n}, universe(n))]
print('psi(n) true for', len(bad), 'of', sum(1 for n in V5 if len(n) <= 2), 'sets n in V_5 with |n| <= 2 (must be 0)')
print('ALL OK' if allok and not bad else 'FAIL')
