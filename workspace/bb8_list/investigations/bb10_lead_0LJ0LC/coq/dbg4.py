from common import *
import mexp
s = G(grp(0, B=1) + [run(Z, k=1)] + list(Z) * 2 + grp(3, n=1) + [1, V('l')])
t = G(grp(1) + [run(Z, k=1)] + list(Z) + grp(4, B=1) + grp(1, n=1) + [1, V('l')])
vals = {'k': 0, 'B': 1, 'n': 0}
def conc(c):
    for v, x in vals.items(): c = mexp.subst(c, v, (), x)
    return c
sc, tc = conc(s), conc(t)
# replay the explorer's stages symbolically, then compare with literal configs
cfg = s; seen = []
for st in range(7):
    ops, cfg, how = mexp.run_stuck(cfg, t)
    seen.append(('stage%d' % st, cfg))
    if how != 'stuck': break
    lp = mexp.find_loop(cfg, 2)
    if lp is None: break
    cfg = lp.after(); seen.append(('after%d' % st, cfg))
targets = {name: pl.canon(conc(c)) for name, c in seen}
c = sc; ct = pl.canon(tc)
for i in range(3000):
    cc = pl.canon(c)
    for name, x in targets.items():
        if cc == x: print('literal step', i, 'matches', name)
    if cc == ct: print('literal step', i, 'TARGET'); break
    c = pl.step(c)
