"""Phase driver: run the explorer until it is stuck without a loop; regroup runs between phases."""
import sys
from common import *
import mexp
from planner8 import is_run, norm_side


def drive(cfg, maxst=60, verbose=True):
    """returns (end cfg, how) with how in stuck/halt"""
    for _ in range(maxst):
        ops, cfg, how = mexp.run_stuck(cfg)
        if how != 'stuck':
            return cfg, how
        lp = mexp.find_loop(cfg, 2)
        if lp is None:
            return cfg, 'stuck'
        if verbose:
            print('   loop on %s' % lp.v_at, file=sys.stderr)
        cfg = lp.after()
    return cfg, 'maxst'


def regroup(cfg, var, k, c, new):
    """substitute var := k*new + c; a run blk^(a*var + rest) becomes blk^c*a (concrete, nearest first) then
    (blk^k)^(a*new) when rest is empty."""
    q, L, R, mode = cfg

    def side(s):
        out = []
        for t in s:
            if is_run(t) and any(v == var for v, _ in t[2]):
                cnt = dict(t[2]); a = cnt.pop(var)
                if cnt:
                    raise ValueError('mixed run %r' % (t,))
                out.extend(list(t[1]) * (a * c))
                out.append(('run', tuple(t[1]) * k, ((new, a),)))
            else:
                out.append(t)
        return norm_side(out)
    return (q, side(L), side(R), mode)


def head_run(cfg):
    q, L, R, mode = cfg
    side = R if mode == '>' else L
    t = side[0]
    if is_run(t) and len(t[2]) == 1 and t[2][0][1] == 1:
        return t[2][0][0]
    return None


def drive_peel(cfg, peelable, maxpeel=40, verbose=True):
    """drive; when stuck reading a run of a peelable variable v, substitute v := v + 1 (fresh name kept = v).
    Returns (cfg, how, peels) with peels = {v: count}."""
    peels = {}
    for _ in range(maxpeel + 1):
        cfg, how = drive(cfg, verbose=verbose)
        if how != 'stuck':
            return cfg, how, peels
        v = head_run(cfg)
        if v is None or v not in peelable:
            return cfg, how, peels
        cfg = engine.subst(cfg, v, ((v, 1),), 1)
        peels[v] = peels.get(v, 0) + 1
        if verbose:
            print('   peel %s (total %d)' % (v, peels[v]), file=sys.stderr)
    return cfg, 'maxpeel', peels
