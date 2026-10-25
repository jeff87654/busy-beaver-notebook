from common import *
import mexp, sys
orig_find = mexp.find_loop
s = G(grp(0, B=1) + [run(Z, k=1)] + list(Z) * 2 + grp(3, n=1) + [1, V('l')])
t = G(grp(1) + [run(Z, k=1)] + list(Z) + grp(4, B=1) + grp(1, n=1) + [1, V('l')])
def explore(start, target, depth=2, splits=6, positive=frozenset(), path='root', maxstages=60):
    cfg = start
    for st in range(maxstages):
        a = cfg
        ops, cfg, how = mexp.run_stuck(cfg, target)
        print(path, 'stage', st, how, ' '.join(o[0] if o[0] != 'steps' else 's%d' % o[1] for o in ops)[:200])
        print('    from', pl.show(a)[:250]); print('    to  ', pl.show(cfg)[:250])
        if how == 'target': return True
        if how == 'halt': print('HALT'); return False
        lp = mexp.find_loop(cfg, depth)
        if lp is not None:
            print('    LOOP on', lp.v_at, 'use', lp.use, 'X=', pl.show(lp.X)[:250])
            cfg = lp.after(); print('    after', pl.show(cfg)[:250]); continue
        if splits <= 0: print('stuck'); return False
        cand = mexp.engine.candidates(cfg)
        cand = [c for c in cand if mexp.coeff_ok(a, c)] or cand
        v = cand[0]; v2 = mexp.fresh(v)
        print('    SPLIT', v)
        if v not in positive:
            if not explore(mexp.subst(a, v, (), 0), mexp.subst(target, v, (), 0), depth, splits-1, positive, path+'/%s=0' % v): return False
        return explore(mexp.subst(a, v, ((v2,1),), 1), mexp.subst(target, v, ((v2,1),), 1), depth, splits-1, positive, path+'/%s=S' % v)
explore(s, t, positive=frozenset(['B']))
