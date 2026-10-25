import pickle
from common import *
import mexp, rules
from hop import XH, S1
from st0a import START as P0_START
from st0b import START as E0W
from mr import MR, S as MR_FIRST
from st2c import S2P, T2
from st3e import S3E, T3E
from st3y import Y_START, Y_TARGET
SUB = engine.subst
def ends(node, acc):
    for it in node['items']:
        if it[0] == 'split':
            for b in (it[3], it[4]):
                if b is not None: ends(b, acc)
    if 'end' in node and not node.get('halt'): acc.append((node['end'], node['target']))
    return acc
def tri(c):
    q, L, s, R = pl.triple(c)
    return coqgen.cfg_coq((q, [s] + list(L), R, '<')) if s in (0, 1) else coqgen.cfg_coq(c)
items = [('F' + n, s, t, p, 2) for n, s, t, p in rules.ITEMS]
items += [('P0', P0_START, S1, (), 0),
          ('P0B', SUB(S1, 'J', (('J', 1),), 1), SUB(SUB(XH('J', 'i'), 'i', (), 1), 'J', (('J', 1),), 0), (), 0),
          ('P0C', SUB(XH(), 'k', (), 0), pickle.load(open('E0cfg.pkl', 'rb')), (), 0),
          ('P0D', E0W, MR_FIRST, (), 0), ('MR1', SUB(MR(), 'w', (('w', 1),), 1), MR(d9=4, rz=8), (), 0),
          ('P0E', SUB(MR(), 'w', (), 0), KF(tok(1), tok(0), list(Z) * 7 + [run(Z, i=1)] + tok(7) + tok(6) + tok(8) + [V('l')]), (), 0),
          ('ST2', S2P, T2, (), 0), ('ST3E', S3E, T3E, (), 0), ('Y1', Y_START, Y_TARGET, ('a',), 6)]
for name, s, t, pos, sp in items:
    tree = mexp.explore(s, t, splits=sp, positive=frozenset(pos))
    for a, b in ends(tree, []):
        same = coqgen.cfg_coq(a) == coqgen.cfg_coq(b)
        print(name, 'SAME' if same else ('MODE' if tri(a) == tri(b) else 'DIFF'))
        if not same and tri(a) != tri(b):
            print('  end:', coqgen.cfg_coq(a)[:900]); print('  tgt:', coqgen.cfg_coq(b)[:900])
