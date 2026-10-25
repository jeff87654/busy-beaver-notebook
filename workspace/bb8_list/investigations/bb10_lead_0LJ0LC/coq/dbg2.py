from common import *
import mexp, sys
cases = {
 'R2': (G(grp(0, B=1) + list(Z) + grp(3, n=1) + [1, V('l')]), G(grp(1) + grp(4, B=1) + grp(1, n=1) + [1, V('l')])),
 'R3': (G(grp(0, B=1) + [run(Z, k=1)] + list(Z) * 2 + grp(3, n=1) + [1, V('l')]),
        G(grp(1) + [run(Z, k=1)] + list(Z) + grp(4, B=1) + grp(1, n=1) + [1, V('l')])),
 'R2z': (G(grp(0, B=1) + list(Z) + grp(2) + [1, BLANK]), G(grp(1) + grp(4, B=1) + grp(0) + [1, BLANK])),
 'R3z': (G(grp(0, B=1) + [run(Z, k=1)] + list(Z) * 2 + grp(2) + [1, BLANK]),
         G(grp(1) + [run(Z, k=1)] + list(Z) + grp(4, B=1) + grp(0) + [1, BLANK])),
}
for name in sys.argv[1].split(','):
    s, t = cases[name]
    for pos in (['B'], ['B', 'k']):
        try:
            tree = mexp.explore(s, t, positive=frozenset(pos))
            print(name, pos, 'OK')
            break
        except Exception as e:
            print(name, pos, 'FAIL', str(e)[:300])
