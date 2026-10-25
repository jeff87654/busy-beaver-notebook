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
