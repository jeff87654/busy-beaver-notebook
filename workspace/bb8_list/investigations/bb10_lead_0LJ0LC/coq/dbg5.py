from common import *
import mexp, sys
s = G(grp(0, B=1) + [run(Z, k=1)] + list(Z) * 2 + grp(3, n=1) + [1, V('l')])
t = G(grp(1) + [run(Z, k=1)] + list(Z) + grp(4, B=1) + grp(1, n=1) + [1, V('l')])
vals = eval(sys.argv[1])
def conc(c):
    for v, x in vals.items(): c = mexp.subst(c, v, (), x)
    return c
cfg = s; seen = []
for st in range(12):
    ops, cfg, how = mexp.run_stuck(cfg, t)
    seen.append(('stage%d' % st, cfg))
    if how != 'stuck': print('how', how); break
    lp = mexp.find_loop(cfg, 2)
    if lp is None: print('no loop at stage', st, pl.show(cfg)); break
    cfg = lp.after(); seen.append(('after%d' % st, cfg))
targets = {name: pl.canon(conc(c)) for name, c in seen}
c = conc(s); ct = pl.canon(conc(t))
for i in range(30000):
    cc = pl.canon(c)
    for name, x in targets.items():
        if cc == x: print('literal step', i, 'matches', name)
    if cc == ct: print('literal step', i, 'TARGET'); break
    c = pl.step(c)
