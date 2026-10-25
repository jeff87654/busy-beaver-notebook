from common import *
def cnt(v, k):  # helper to build runs with constant offsets
    return v, k
def seg(pv, pk, qv, qk):
    # returns left tokens for (01)^(pv+pk) (10)^(qv+qk)
    out = mkrun(B_, {qv: 1} if qv else {}, qk) + mkrun(A_, {pv: 1} if pv else {}, pk)
    return out
S = ('A', pl.norm_side(seg('y', 0, 'x', 2) and (mkrun(B_, {'y': 1}, 0) + mkrun(A_, {'x': 1}, 2)) + [V('l')]), [0, 1, BLANK], '>')
Tg = ('A', pl.norm_side(mkrun(B_, {'y': 1}, 4) + mkrun(A_, {'x': 1}, 0) + [V('l')]), [0, 1, BLANK], '>')
print(pl.show(S)); print(pl.show(Tg))
tree = engine.explore(S, Tg)
print(engine.describe(tree))
