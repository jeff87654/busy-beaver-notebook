import sys, io, contextlib
sys.argv = ['x', '19']
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    import dbg_d2
import mexp, engine
from planner8 import show
S = dbg_d2.cfg
v = 'q'
v2 = mexp.fresh(v)
P = mexp.subst(S, v, ((v2, 1),), 1)
S1 = mexp.subst(S, v, ((v2, 1),), 0)
ops, C, how = mexp.run_stuck(P)
m = mexp.match_shift_multi(S1, C)
print('inserts', m)
X, vg, ivs = mexp.generalize(S, v, m)
print('X =', show(X)[:900])
vg2 = mexp.fresh(vg)
Xp = mexp.subst(X, vg, ((vg2, 1),), 1)
Xt = mexp.subst(X, vg, ((vg2, 1),), 0)
for iv in ivs:
    Xt = mexp.subst(Xt, iv, ((iv, 1),), 1)
cfg = Xp
for k in range(6):
    ops, cfg, how = mexp.run_stuck(cfg, Xt)
    print(k, how, sum(o[1] for o in ops if o[0]=='steps'), show(cfg)[:900])
    if how != 'stuck': break
    lp = mexp.find_loop(cfg, 1, verbose=True)
    print('  inner', lp and (lp.v_at, lp.use_arg()))
    if lp is None: break
    cfg = lp.after()
