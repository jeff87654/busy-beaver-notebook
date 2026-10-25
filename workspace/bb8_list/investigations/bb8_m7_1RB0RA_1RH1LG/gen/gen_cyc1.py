import sys, time
from common import *
from shapes import *
import mexp
c, a1 = '110', '10'
TAILC = c + '1111' + c + '0' + a1 + '0' + '1'
def st(bits): return [int(ch) for ch in reversed(bits)]
START = ('B', st(TAILC) + [run((1,), N=1)] + [0, V('l')], [BLANK], '>')
TARGET = ('B', st(TAILC) + [run((1,), N=1)] + [1, 1] + [0, V('l')], [BLANK], '>')
pl.LEMMAS.clear()
t0 = time.time()
tree = mexp.explore(START, TARGET, splits=2)
g = mexp.Gen('CY')
rule = mexp.rule_lemma('CYCLE', START, TARGET, tree, g, progress=True)
print('CYCLE: %d lemmas (%.1fs)' % (len(g.lemmas), time.time() - t0))
text = header('cycle') + '\n' + coqgen.crossing_lemmas() + '\n' + '\n'.join(g.lemmas) + '\n' + rule
open('cycle.v', 'w', newline='\n').write(text)
