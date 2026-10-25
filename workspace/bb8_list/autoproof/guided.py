"""Debug helper: follow engine.explore's branches that agree with concrete values, comparing with literal runs."""
import planner8 as pl
from planner8 import show
import engine, validate


def guided(start, target, vals, stages=30):
    vals = dict(vals)
    N = validate.reaches(start, target, vals)
    print('literal: target after', N, 'steps')
    cfg, tgt = start, target
    for stage in range(stages):
        ops, c2, how = engine.run_until_stuck(cfg, None, target=tgt)
        n = validate.reaches(start, c2, vals)
        print('stage %d %s: at literal step %s | %s' % (stage, how, n, show(c2)))
        cfg = c2
        if how != 'stuck':
            return how
        lp = engine.accelerate(cfg, 1)
        if lp is not None:
            v, v2 = lp['v'], lp['v2']
            if vals.get(v, 0) == 0:
                cfg, tgt = engine.subst(cfg, v, (), 0), engine.subst(tgt, v, (), 0)
                print('   loop on %s, branch %s=0' % (v, v))
            else:
                vals[v2] = vals[v] - 1
                cfg, tgt = lp['resultB'], engine.subst(tgt, v, ((v2, 1),), 1)
                print('   loop on %s, %s rounds -> literal step %s | %s' % (v, vals[v2], validate.reaches(start, cfg, vals), show(cfg)))
            continue
        _, why = pl.try_crossing(cfg)
        cand = engine.candidates(cfg, behind_first=bool(why) and why.startswith('left known region'))
        if not cand:
            print('   no candidate'); return 'stuck'
        v = cand[0]
        if vals.get(v, 0) == 0:
            cfg, tgt = engine.subst(cfg, v, (), 0), engine.subst(tgt, v, (), 0); print('   split %s -> 0' % v)
        else:
            v2 = engine.fresh(v); vals[v2] = vals[v] - 1
            cfg, tgt = engine.subst(cfg, v, ((v2, 1),), 1), engine.subst(tgt, v, ((v2, 1),), 1); print('   split %s -> S' % v)
