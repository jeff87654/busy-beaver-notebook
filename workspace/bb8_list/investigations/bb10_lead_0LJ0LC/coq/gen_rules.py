"""Machine-level rules R1, R23 on the n-list family (general rest l)."""
import sys, time
from common import *
import mexp
ITEMS = [
    # R1: (B units ; n+2 ; l) -->+ (B+4 ; n ; l)   (B = 2b+1: b -> b+2)
    ('R1', G(grp(0, B=1) + grp(2, n=1) + [V('l')]), G(grp(4, B=1) + grp(0, n=1) + [V('l')]), ()),
    # R23: (B ; 0^(k+1) ; n+3 ; l) -->+ (1 ; 0^k ; B+4 ; n+1 ; l)
    ('R23', G(grp(0, B=1) + [run(Z, k=1)] + list(Z) + grp(3, n=1) + [1, V('l')]),
            G(grp(1) + [run(Z, k=1)] + grp(4, B=1) + grp(1, n=1) + [1, V('l')]), ('B',)),
    # R23z (top entry 2 -> 0; the machine reads the leading 1 behind it):
    #   (B ; 0^(k+1) ; 2 ; 1 0^inf) -->+ (1 ; 0^k ; B+4 ; 0 ; 1 0^inf)
    ('R23z', G(grp(0, B=1) + [run(Z, k=1)] + list(Z) + grp(2) + [1, BLANK]),
             G(grp(1) + [run(Z, k=1)] + grp(4, B=1) + grp(0) + [1, BLANK]), ('B',)),
]
if __name__ == '__main__':
    pl.LEMMAS.clear()
    lemmas, rules = [], []
    for name, s, t, pos in ITEMS:
        t0 = time.time()
        tree = mexp.explore(s, t, positive=frozenset(pos))
        if '-v' in sys.argv:
            print('\n'.join(mexp.describe(tree)))
        g = mexp.Gen(name)
        rules.append(mexp.rule_lemma(name, s, t, tree, g, progress=True, positive=pos))
        lemmas.extend(g.lemmas)
        print('%s: %d lemmas (%.1fs)' % (name, len(g.lemmas), time.time() - t0))
    text = header('rules test') + '\n' + coqgen.crossing_lemmas() + '\n' + '\n'.join(lemmas) + '\n' + '\n'.join(rules)
    open(sys.argv[1], 'w', newline='\n').write(text)
