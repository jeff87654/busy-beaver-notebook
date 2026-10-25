"""Dev test: rules + abstract part, with the big machine lemmas stated and Admitted (NOT a proof)."""
import re, sys
from pathlib import Path
from common import *
import mexp, gen_rules
pl.LEMMAS.clear()
lemmas = []
for name, s, t, pos in gen_rules.ITEMS:
    tree = mexp.explore(s, t, positive=frozenset(pos))
    g = mexp.Gen(name)
    lemmas += g.lemmas + [mexp.rule_lemma(name, s, t, tree, g, progress=True, positive=pos)]
full = Path('T_full.v').read_text()
stubs = []
for nm in ('REBUILD', 'D2STAGE', 'HALTRUN', 'HALTED'):
    m = re.search(r'^Lemma %s : .*?\.\n' % nm, full, re.M | re.S)
    stubs.append(m.group(0) + 'Admitted.\n')
text = header('abstract test') + '\n' + coqgen.crossing_lemmas() + '\n'.join(lemmas) + '\n' + '\n'.join(stubs) + Path('abstract.v.in').read_text()
Path('T_abs.v').write_text(text, newline='\n')
