"""gen_ev.py OUT.v NAME=pickle [NAME=pickle ...]: re-explore each pickled (start, target) and emit its Coq rule lemma NAME."""
import sys, pickle
from common import *
import d0spec, mexp
out = sys.argv[1]
pl.LEMMAS.clear()
lemmas = []
for a in sys.argv[2:]:
    name, pk = a.split('=')
    S, Tg, _ = pickle.load(open(pk, 'rb'))
    tree = mexp.explore(S, Tg, splits=0)
    g = mexp.Gen(name.replace('_', ''))
    lemmas += g.lemmas + [mexp.rule_lemma(name, S, Tg, tree, g, progress=True)]
    print('%s: %d lemmas' % (name, len(g.lemmas)))
text = header('C04 machine lemmas') + '\n' + coqgen.crossing_lemmas() + '\n' + '\n'.join(lemmas)
open(out, 'w', newline='\n').write(text)
print('wrote', out, len(text))
