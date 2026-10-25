import sys, time
from rules_def import *
name = sys.argv[1]
s, t = RULES[name]
tree = engine.explore(s, t)
gen = coqgen.RuleGen(name, engine)
try:
    txt = coqgen.rule_lemma(name, s, t, tree, gen, progress=True)
    print(name, 'OK', len(gen.lemmas))
except Exception as e:
    print(name, 'GENFAIL', e)
