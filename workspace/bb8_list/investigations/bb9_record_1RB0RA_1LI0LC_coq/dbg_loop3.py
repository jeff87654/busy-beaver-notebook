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
for i in (1, 2):
    a, b = mexp.side_tokens(S1[i]), mexp.side_tokens(C[i])
    print(i, len(a), len(b))
    print('  s:', a[:60])
    print('  c:', b[:66])
    print('  ->', mexp.match_side_multi(a, b))
