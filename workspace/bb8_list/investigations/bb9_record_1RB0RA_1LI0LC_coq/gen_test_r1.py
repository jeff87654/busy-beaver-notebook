import sys, time
from common import *
import mexp
def left(acc, atok):
    return [1, 0, 0, 1, run(TB, t=1), 1, 1] + acc + [1] + atok + [V('l')]
start = ('B', left([run((0, 1), r=1)], [0, 1] * 3 + [run((0, 1), m=1)]), [BLANK], '>')
target = ('B', left([0, 1] * 4 + [run((0, 1, 0, 1), r=1)], [run((0, 1), m=1)]), [BLANK], '>')
pl.LEMMAS.clear()
t0 = time.time()
tree = mexp.explore(start, target, positive=frozenset(['r']))
print('\n'.join(mexp.describe(tree)))
print('explore %.1fs' % (time.time() - t0))
g = mexp.Gen('R1')
rule = mexp.rule_lemma('R1', start, target, tree, g, progress=True, positive=('r',))
text = header('test R1') + '\n' + coqgen.crossing_lemmas() + '\n' + '\n'.join(g.lemmas) + '\n' + rule
open(sys.argv[1], 'w', newline='\n').write(text)
print(len(g.lemmas), 'lemmas')
