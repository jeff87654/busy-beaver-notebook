"""R1 exhaustion #1 rebuild for C04: Kt(1^11;1;A;0) -->+ Kt(0,0,7,1^(4A+16);1;2;3), accumulator A = a+5 (a free).
   The far 0,0 is the frame [1;1;BLANK] of KK.  At the use site A = 3 Bx + 2."""
import sys, time
from common import *
from shapes import *
import mexp
def KK(tcount, acc, atok, mid):
    return ('B', [1, 0, 0, 1] + list(TB) * tcount + [1, 1] + acc + atok + mid + [1, 1, BLANK], [BLANK], '>')
START = KK(0, accr(5, 'a', (0, 1)), tok(1), list(Z) * 11)
TARGET = KK(3, accr(2), tok(1), list(Z) * 36 + [run(Z * 4, a=1)] + tok(7))
def gen():
    t0 = time.time()
    tree = mexp.explore(START, TARGET, splits=0, maxstages=400)
    g = mexp.Gen('RB1')
    rule = mexp.rule_lemma('REBUILD1', START, TARGET, tree, g, progress=True)
    print('rebuild1: %d lemmas (%.0fs)' % (len(g.lemmas), time.time() - t0), file=sys.stderr)
    return g.lemmas, rule
if __name__ == '__main__':
    pl.LEMMAS.clear()
    lem, rule = gen()
    text = header('rebuild1 test') + '\n' + coqgen.crossing_lemmas() + '\n' + '\n'.join(lem) + '\n' + rule
    open(sys.argv[1], 'w', newline='\n').write(text)
