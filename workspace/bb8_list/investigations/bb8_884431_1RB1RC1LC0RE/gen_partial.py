"""Partial busycoq proof for 1RB1RC_1LC0RE_1LF1LD_1LA1LE_1RH1RF_0LF1LG_0LD1LA_---0RA (R1, R2 proved, R3/R4 TODO)."""
import sys
sys.path.insert(0, '.')
from rules884 import *
import engine, coqgen, coqgen_util
from pathlib import Path

pl.set_tm(TM)
pl.LEMMAS.clear()
lemmas, rule_texts = [], []
import rules_r4
items = [(n, s, t, True) for n, s, t in rules() if n in ('R1m', 'R2m')]   # + rules_r4.pieces(): R4b needs nested loops
for name, start, target, prog in items:
    tree = engine.explore(start, target)
    gen = coqgen.RuleGen(name, engine)
    rule_texts.append(coqgen.rule_lemma(name, start, target, tree, gen, progress=prog))
    lemmas.extend(gen.lemmas)
    print(name, 'ok', file=sys.stderr)
head = Path('header.v.in').read_text().replace('@TITLE@', 'BB(8) holdout 884431: ' + TM + ' (PARTIAL: R3/R4 machine-level rules TODO)') \
    .replace('@N@', '8').replace('@TM@', TM).replace('@TABLE@', coqgen_util.table(TM))
fam = Path('family_884431.v.in').read_text()
text = head + '\n(** ** Crossing lemmas (generated) *)\n\n' + coqgen.crossing_lemmas() \
    + '\n(** ** Stage and loop lemmas (generated) *)\n\n' + '\n'.join(lemmas) \
    + '\n(** ** Machine-level rules R1m, R2m (generated) *)\n\n' + '\n'.join(rule_texts) + '\n' + fam
Path(sys.argv[1]).write_text(text, newline='\n')
print('wrote', sys.argv[1], file=sys.stderr)
