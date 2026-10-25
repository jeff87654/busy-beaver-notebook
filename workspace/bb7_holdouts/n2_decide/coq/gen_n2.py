"""Generate the machine-level rule lemmas for N2 with bb8_list/autoproof.  python gen_n2.py OUT_rules.v.part"""
import sys, time
from rules_def import *
import coqgen_util
from pathlib import Path
AUTO = Path(r'C:\Users\jeffr\Downloads\bb8\bb8_list\autoproof')
def header(title):
    return (AUTO / 'header.v.in').read_text().replace('@TITLE@', title).replace('@N@', '7') \
        .replace('@TM@', TM).replace('@TABLE@', coqgen_util.table(TM))
ORDER = [('R1', True), ('R2', True), ('R6b', True), ('R8b', True),
         ('R4s0', True), ('R4s1', True), ('R6s', True), ('L1', True), ('R4b', True), ('L2', True), ('R4c', True), ('L3', True),
         ('R4d', True), ('E1', True), ('D3O', True), ('D2E', True), ('D3E', True), ('D3EL', True), ('D3E0', True), ('D0E', True)]
pl.LEMMAS.clear()
lemmas, rules = [], []
for name, prog in ORDER:
    s, t = RULES[name]
    t0 = time.time()
    tree = engine.explore(s, t)
    gen = coqgen.RuleGen(name, engine)
    rules.append(coqgen.rule_lemma(name, s, t, tree, gen, progress=prog))
    lemmas.extend(gen.lemmas)
    print('  %s: %d lemmas (%.1fs)' % (name, len(gen.lemmas), time.time() - t0), file=sys.stderr)
text = header('BB(7) holdout N2: ' + TM + ' never halts') \
    + '\n(** ** Crossing lemmas (generated) *)\n\n' + coqgen.crossing_lemmas() \
    + '\n(** ** Stage and loop lemmas (generated) *)\n\n' + '\n'.join(lemmas) \
    + '\n(** ** Machine-level rules (generated) *)\n\n' + '\n'.join(rules) + '\n'
Path(sys.argv[1]).write_text(text, newline='\n')
print('wrote', sys.argv[1], file=sys.stderr)
