"""val_items.py GROUP...: literal check (validate.reaches) of each group item on random parameter values."""
import sys, random
from common import *
import validate, engine
for g in sys.argv[1:]:
    mod = __import__('grp_' + g)
    for name, S, T, kw, pos in mod.ITEMS:
        vs = sorted(engine.vars_of(S) | engine.vars_of(T))
        rnd = random.Random(7); bad = 0; n = 0
        for trial in range(12):
            vals = {v: rnd.choice([0, 1, 2, rnd.randint(3, 9), rnd.randint(10, 25)]) for v in vs}
            for v in pos: vals[v] = max(vals[v], 1)
            r = validate.reaches(S, T, vals, max_steps=30_000_000)
            n += 1
            if r is None: bad += 1; print('  FAIL', name, vals)
        print(name, 'vars', vs, 'bad', bad, 'of', n, flush=True)
