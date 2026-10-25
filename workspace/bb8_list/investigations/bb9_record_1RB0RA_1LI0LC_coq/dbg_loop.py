import sys, io, contextlib
sys.argv = ['x', '19']
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    import dbg_d2
import mexp, engine
from planner8 import show
S = dbg_d2.cfg
print('S =', show(S)[:400])
for S2, v, use in mexp.absorb_variants(S):
    print('variant', v, use, show(S2)[:200])
    v2 = mexp.fresh(v)
    P = mexp.subst(S2, v, ((v2, 1),), 1)
    S1 = mexp.subst(S2, v, ((v2, 1),), 0)
    cfg = P
    for it in range(4):
        ops, C, how = mexp.run_stuck(cfg)
        print('  round part', it, how, sum(o[1] for o in ops if o[0]=='steps'), show(C)[:400])
        m = engine.match_shift(S1, C)
        print('  match', m)
        if m is not None or how != 'stuck': break
        inner = mexp.find_loop(C, 1)
        print('  inner', inner and (inner.v_at, inner.use_arg()))
        if inner is None: break
        cfg = inner.after()
