from rules_def import *
import sys
nm = sys.argv[1]
S, Tg = RULES[nm]
print(pl.show(S)); print(pl.show(Tg))
tree = engine.explore(S, Tg)
for l in engine.describe(tree): print(l)
