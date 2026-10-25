"""Hand-specified transfer loops for mexp: X(v, i) with loop variable v and stack variables ivs."""
from common import *
import mexp
subst = engine.subst


def make_loop(X, vg, ivs, use, S=None, depth=2, maxloops=200):
    """round X(S v2, i..) -->* X(v2, S i..) explored by mexp.run_round; use = (lin form, const) for v at the use site
    (stacks start at 0).  S = configuration at the use site (default X with vg := use, ivs := 0)."""
    vg2 = mexp.fresh(vg)
    Xp = subst(X, vg, ((vg2, 1),), 1)
    Xt = subst(X, vg, ((vg2, 1),), 0)
    for iv in ivs:
        Xt = subst(Xt, iv, ((iv, 1),), 1)
    segs = mexp.run_round(Xp, Xt, depth, maxloops)
    if segs is None:
        raise mexp.Fail('hand loop: round does not close')
    lp = mexp.Loop(X=X, vg=vg, vg2=vg2, ivs=list(ivs), Xp=Xp, Xt=Xt, segs=segs, v_at=vg, use=use)
    if S is None:
        form, const = use
        S = X
        for iv in ivs:
            S = subst(S, iv, (), 0)
        S = subst(S, vg, form, const)
    lp.S = S
    return lp
