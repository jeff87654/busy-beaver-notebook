from common import *
import mexp, sys
def R23(fix):
    s = G(grp(0, B=1) + [run(Z, k=1)] + list(Z) + grp(3, n=1) + [1, V('l')])
    t = G(grp(1) + [run(Z, k=1)] + grp(4, B=1) + grp(1, n=1) + [1, V('l')])
    for v, val in fix.items():
        s = mexp.subst(s, v, (), val); t = mexp.subst(t, v, (), val)
    return s, t
for fix in eval(sys.argv[1]):
    s, t = R23(fix)
    try:
        tree = mexp.explore(s, t, positive=frozenset(['B']) - set(fix))
        print(fix, 'OK')
        if len(sys.argv) > 2: print('\n'.join(mexp.describe(tree)))
    except Exception as e:
        print(fix, 'FAIL', str(e)[:300])
