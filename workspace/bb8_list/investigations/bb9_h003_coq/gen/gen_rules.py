"""Machine-level champion rules R1-R3 on the token family (general tail t, rest of the list l)."""
import sys, time
from common import *
from shapes import *
import mexp
ITEMS = [
    # R1: Kt ds (m+3) r t -->+ Kt ds m (2r+4) t   (r >= 1)
    ('R1', K(accr(0, 'r'), tok(3, 'm'), []), K(accr(4, 'r', (0, 1, 0, 1)), tok(0, 'm'), []), ('r',)),
    # R2: Kt (x+3 :: ds) 1 r t -->+ Kt (x :: ds) (2r+3) 2 t   (r >= 1)
    ('R2', K(accr(0, 'r'), tok(1), tok(3, 'x')), K(accr(2), tok(3, 'r', (0, 1, 0, 1)), tok(0, 'x')), ('r',)),
    # R3: Kt (1^(k+1) ++ (x+3) :: ds) 1 r t -->+ Kt (1^k ++ (2r+3) :: x :: ds) 1 2 t   (r >= 1)
    ('R3', K(accr(0, 'r'), tok(1), list(Z) + [run(Z, k=1)] + tok(3, 'x')),
           K(accr(2), tok(1), [run(Z, k=1)] + tok(3, 'r', (0, 1, 0, 1)) + tok(0, 'x')), ('r', 'x')),
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
