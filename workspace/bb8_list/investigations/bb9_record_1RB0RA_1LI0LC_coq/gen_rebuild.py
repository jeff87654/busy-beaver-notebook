"""Rebuild: Kt (repeat 1 11) 1 (r+5) 0 -->* Kt (repeat 1 (4r+1) ++ [20;4;21;4]) 1 2 6 (machine level)."""
import sys, time
from common import *
from shapes import *
import mexp


def KK(tcount, acc, atok, mid):
    return ('B', [1, 0, 0, 1] + list(TB) * tcount + [1, 1] + acc + atok + mid + [1, 1, BLANK], [BLANK], '>')


START = KK(0, accr(5, 'r'), tok(1), list(Z) * 11)
TARGET = KK(6, accr(2), tok(1), list(Z) + [run(Z * 4, r=1)] + tok(20) + tok(4) + tok(21) + tok(4))


def gen():
    t0 = time.time()
    tree = mexp.explore(START, TARGET, splits=0)
    g = mexp.Gen('RB')
    rule = mexp.rule_lemma('REBUILD', START, TARGET, tree, g, progress=True)
    print('rebuild: %d lemmas (%.1fs)' % (len(g.lemmas), time.time() - t0), file=sys.stderr)
    return g.lemmas, rule


if __name__ == '__main__':
    pl.LEMMAS.clear()
    lem, rule = gen()
    text = header('rebuild test') + '\n' + coqgen.crossing_lemmas() + '\n' + '\n'.join(lem) + '\n' + rule
    open(sys.argv[1], 'w', newline='\n').write(text)
