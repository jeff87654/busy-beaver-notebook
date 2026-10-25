"""R2z / R3z: the champion rules R2 / R3 when the borrowed token is followed (far side) by a gap 00 instead of a token."""
import sys, time
from common import *
from shapes import *
import mexp
def Kz(acc, atok, rest):
    return ('B', tailpart() + acc + atok + rest + [0, 0, V('l')], [BLANK], '>')
ITEMS = [
    ('R2z', Kz(accr(0, 'r'), tok(1), tok(3, 'x')), Kz(accr(2), tok(3, 'r', (0, 1, 0, 1)), tok(0, 'x')), ('r',)),
    ('R3z', Kz(accr(0, 'r'), tok(1), list(Z) + [run(Z, k=1)] + tok(3, 'x')),
            Kz(accr(2), tok(1), [run(Z, k=1)] + tok(3, 'r', (0, 1, 0, 1)) + tok(0, 'x')), ('r',)),
]
if __name__ == '__main__':
    pl.LEMMAS.clear()
    lemmas = []
    for name, s, t, pos in ITEMS:
        tree = mexp.explore(s, t, positive=frozenset(pos))
        g = mexp.Gen(name)
        lemmas += g.lemmas + [mexp.rule_lemma(name, s, t, tree, g, progress=True, positive=pos)]
        print(name, len(g.lemmas))
    open(sys.argv[1], 'w', newline='\n').write(header('rules z') + '\n' + coqgen.crossing_lemmas() + '\n' + '\n'.join(lemmas))
