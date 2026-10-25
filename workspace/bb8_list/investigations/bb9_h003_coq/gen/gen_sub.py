"""gen_sub.py OUT.v C E [C E ...]: Coq lemmas for SUB (L = 5j+C) with parked P = 6p + E + 12 (test file)."""
import sys, time, pickle
from common import *
import d0spec, mexp
out = sys.argv[1]; args = sys.argv[2:]
pl.LEMMAS.clear()
lemmas = []
for k in range(0, len(args), 2):
    C, E = int(args[k]), int(args[k + 1])
    S, Tg, _ = pickle.load(open('tree_sub_%d_%d.pkl' % (C, E), 'rb'))
    tree = mexp.explore(S, Tg, splits=0)
    g = mexp.Gen('S%d_%d' % (C, E))
    rule = mexp.rule_lemma('SUB%d_%d' % (C, E), S, Tg, tree, g, progress=True)
    lemmas += g.lemmas + [rule]
    print('SUB%d_%d: %d lemmas' % (C, E, len(g.lemmas)))
text = header('C04 sub-step test') + '\n' + coqgen.crossing_lemmas() + '\n' + '\n'.join(lemmas)
open(out, 'w', newline='\n').write(text)
print('wrote', out, len(text))
