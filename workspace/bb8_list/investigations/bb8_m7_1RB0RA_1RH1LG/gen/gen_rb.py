import sys, time, traceback
from common import *
from shapes import *
from gen_all import KB, U3
import mexp
U6 = (0, 1) * 6
START = ('B', tailpart() + accr(2) + [run(U3, b=1)] + tok(1) + [run(Z, n=1)] + [1, 1, BLANK], [BLANK], '>')
TARGET = KB(accr(2), tok(1), [run(Z, n=1)] + list(Z) + tok(5, 'b', U6))
if __name__ == '__main__':
    pos = frozenset(sys.argv[2].split(',')) if len(sys.argv) > 2 and sys.argv[2] != '-' else frozenset()
    pl.LEMMAS.clear()
    t0 = time.time()
    tree = mexp.explore(START, TARGET, positive=pos)
    print(' '.join(mexp.describe(tree))[:1500] if '-v' in sys.argv else '', flush=True)
    g = mexp.Gen('RB')
    rule = mexp.rule_lemma('REBUILD', START, TARGET, tree, g, progress=True, positive=tuple(pos))
    print('REBUILD: %d lemmas (%.1fs)' % (len(g.lemmas), time.time() - t0), flush=True)
    text = header('rebuild') + '\n' + coqgen.crossing_lemmas() + '\n' + '\n'.join(g.lemmas) + '\n' + rule
    open(sys.argv[1], 'w', newline='\n').write(text)
