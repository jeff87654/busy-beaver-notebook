"""Machine-level lemmas of the used-up transient (13 tokens D(1), r = 3b+2) -> cycler."""
import sys, time
from ms3 import *
ITEMS = [
    ('U1', M0, Y0, True),
    ('U2', Y0, M2, True),
    ('U3', M2, ZB, True),
    ('ZR', ZS, ZT, True),
    ('ZF', Z02, M3k1, True),
    ('U4', M3k1, M4k1, True),
]
def generate():
    lemmas, rules = [], []
    for name, s, t, prog in ITEMS:
        t0 = time.time()
        tree = mexp.explore(s, t)
        g = mexp.Gen(name)
        rules.append(mexp.rule_lemma(name, s, t, tree, g, progress=prog))
        lemmas.extend(g.lemmas)
        print('%s: %d lemmas (%.1fs)' % (name, len(g.lemmas), time.time() - t0), file=sys.stderr)
    return lemmas, rules
if __name__ == '__main__':
    pl.LEMMAS.clear()
    lemmas, rules = generate()
    text = header('transient test') + '\n' + coqgen.crossing_lemmas() + '\n' + '\n'.join(lemmas) + '\n' + '\n'.join(rules)
    open(sys.argv[1], 'w', newline='\n').write(text)
