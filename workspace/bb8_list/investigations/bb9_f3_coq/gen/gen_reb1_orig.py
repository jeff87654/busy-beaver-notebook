import sys, time
import common
from common import *
from shapes import *
import mexp_orig as mexp
def KK(tcount, acc, atok, mid):
    return ('B', [1, 0, 0, 1] + list(TB) * tcount + [1, 1] + acc + atok + mid + [1, 1, BLANK], [BLANK], '>')
START = KK(0, accr(20, 'a', (0, 1)), tok(1), list(Z) * 11)
TARGET = KK(3, accr(2), tok(1), list(Z) * 96 + [run(Z * 4, a=1)] + tok(7) + tok(0) + tok(0))
if __name__ == '__main__':
    pl.LEMMAS.clear()
    t0 = time.time()
    tree = mexp.explore(START, TARGET, splits=0, maxstages=400)
    g = mexp.Gen('RB1')
    rule = mexp.rule_lemma('REBUILD1', START, TARGET, tree, g, progress=True)
    print('rebuild1: %d lemmas (%.0fs)' % (len(g.lemmas), time.time() - t0), file=sys.stderr)
    text = header('rebuild1 test') + '\n' + coqgen.crossing_lemmas() + '\n' + '\n'.join(g.lemmas) + '\n' + rule
    open(sys.argv[1], 'w', newline='\n').write(text)
