from evs import *
import mexp
from planner8 import show
def ends(node):
    out = []
    if 'end' in node: out.append(node['end'])
    for it in node['items']:
        if it[0] == 'split':
            for b in (it[3], it[4]):
                if b is not None: out += ends(b)
    return out
for name in ['H', 'S0', 'P1', 'P2', 'P3', 'P4', 'E']:
    S, T = EV[name][:2]
    pos = frozenset(EV[name][2]) if len(EV[name]) > 2 else frozenset()
    tree = mexp.explore(S, T, splits=4, positive=pos)
    for e in ends(tree):
        same = coqgen.cfg_coq(e) == coqgen.cfg_coq(T)
        print(name, 'SAME' if same else 'DIFF')
        if not same:
            print('   end:', show(e)); print('   tgt:', show(T))
