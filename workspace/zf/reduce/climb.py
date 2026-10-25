"""Hill-climb over clause order (block moves like zf2.py __main__, plus swaps), with random restarts.
usage: python climb.py VARIANT_MODULE:CLASS KEEP(json|-) START_ORDER(json|-) SEED OUT.json"""
import sys, json, random, importlib, os
import lowprio
import zfv
modname, clsname = sys.argv[1].split(':')
cls = getattr(importlib.import_module(modname), clsname)
keep = None if sys.argv[2] == '-' else json.loads(sys.argv[2])
n = len(keep) if keep is not None else len(cls().axioms())
# premise-consuming clauses (DET, GEN) must not be last: identified by class attribute
forbid_last = set(getattr(cls, 'FORBID_LAST', None) or [])
if keep is not None and not forbid_last:
    forbid_last = {i for i, k in enumerate(keep) if k in (0, 1)}
order = list(range(n)) if sys.argv[3] == '-' else json.loads(sys.argv[3])
seed = int(sys.argv[4]); out = sys.argv[5]
rng = random.Random(seed)
if seed:
    rng.shuffle(order)
    while order[-1] in forbid_last: rng.shuffle(order)
def ok(o): return o[-1] not in forbid_last
def c(o): return zfv.cost(o, cls, keep)
best = c(order); print('start', best, order, flush=True)
changed = True
while changed:
    changed = False
    cands = []
    for mid in range(1, n):
        for left in range(mid):
            for right in range(mid + 1, n + 1):
                cands.append(order[:left] + order[mid:right] + order[left:mid] + order[right:])
    if seed: rng.shuffle(cands)
    for no in cands:
        if not ok(no): continue
        v = c(no)
        if v < best:
            best, order, changed = v, no, True
            print(best, order, flush=True)
            if seed: break   # first-improvement for randomized runs
print('final', best, order, flush=True)
json.dump({'count': best, 'order': order, 'keep': keep, 'cls': sys.argv[1]}, open(out, 'w'))
