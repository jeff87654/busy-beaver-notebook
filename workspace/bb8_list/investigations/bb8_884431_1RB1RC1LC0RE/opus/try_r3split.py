import sys, time, traceback
from pieces import *
cases = {'b0': (engine.subst(start3, 'b', (), 0), engine.subst(G3, 'b', (), 0)),
         'bS': (engine.subst(start3, 'b', (('b', 1),), 1), engine.subst(G3, 'b', (('b', 1),), 1)),
         'bSM': (engine.subst(start3, 'b', (('b', 1),), 1), engine.subst(M3, 'b', (('b', 1),), 1)),
         'MbS': (engine.subst(M3, 'b', (('b', 1),), 1), engine.subst(G3, 'b', (('b', 1),), 1))}
for nm in sys.argv[1:]:
    a, b = cases[nm]
    t0 = time.time()
    try:
        tree = engine.explore(a, b)
        print(nm, 'OK %.1fs' % (time.time() - t0)); print('\n'.join(engine.describe(tree)))
        gen = coqgen.RuleGen('X' + nm, engine)
        coqgen.rule_lemma('X' + nm, a, b, tree, gen, progress=True)
        print(nm, 'COQGEN OK', len(gen.lemmas), 'lemmas')
    except Exception:
        print(nm, 'FAIL %.1fs' % (time.time() - t0), traceback.format_exc()[-700:])
