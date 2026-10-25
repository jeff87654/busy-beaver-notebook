"""Machine-level champion rules R1-R3 (+R0, R0z) on the token family with tail T1j (python gen_rules.py OUT.v [T0|T1] [-v])."""
import sys, time
from common import *
import shapes
from shapes import *
import mexp
ITEMS = [
    # R1: (m+3) r -> m (2r+4)
    ('R1', lambda: (K(accr(0, 'r'), tok(3, 'm'), []), K(accr(4, 'r', (0, 1, 0, 1)), tok(0, 'm'), [])), ('r',)),
    # R2: (x+3) 1 r -> x (2r+3) 2
    ('R2', lambda: (K(accr(0, 'r'), tok(1), tok(3, 'x')), K(accr(2), tok(3, 'r', (0, 1, 0, 1)), tok(0, 'x'))), ('r',)),
    # R3: (x+3) 1^(k+1) 1 r -> x (2r+3) 1^k 1 2
    ('R3', lambda: (K(accr(0, 'r'), tok(1), list(Z) + [run(Z, k=1)] + tok(3, 'x')),
                    K(accr(2), tok(1), [run(Z, k=1)] + tok(3, 'r', (0, 1, 0, 1)) + tok(0, 'x'))), ('r', 'x')),
    # R0: (x+4) 0 r -> x (2r+3) 2
    ('R0', lambda: (K(accr(0, 'r'), tok(0), tok(4, 'x')), K(accr(2), tok(3, 'r', (0, 1, 0, 1)), tok(0, 'x'))), ('r',)),
]
if __name__ == '__main__':
    out = sys.argv[1]; shapes.TAIL = sys.argv[2] if len(sys.argv) > 2 else 'T1'
    only = [a for a in sys.argv[3:] if not a.startswith('-')]
    pl.LEMMAS.clear()
    lemmas, rules = [], []
    for name, mk, pos in ITEMS:
        if only and name not in only: continue
        s, t = mk(); name = name + shapes.TAIL
        t0 = time.time()
        try:
            tree = mexp.explore(s, t, positive=frozenset(pos))
        except Exception as e:
            print('%s: FAILED %r' % (name, e)); continue
        if '-v' in sys.argv: print('\n'.join(mexp.describe(tree)))
        g = mexp.Gen(name)
        rules.append(mexp.rule_lemma(name, s, t, tree, g, progress=True, positive=pos))
        lemmas.extend(g.lemmas)
        print('%s: %d lemmas (%.1fs)' % (name, len(g.lemmas), time.time() - t0))
    text = header('rules (tail %s)' % shapes.TAIL) + '\n' + coqgen.crossing_lemmas() + '\n' + '\n'.join(lemmas) + '\n' + '\n'.join(rules)
    open(out, 'w', newline='\n').write(text)
