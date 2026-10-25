"""cmp.py GRID... : compare ctx grids against f1/ctx_M8.tsv per context: SAME (same trace), EXTRA (trace extends M8's and halts),
NOHALT (STOP/END), DIFF (other halts).  Prints counts and the minimum ones delta in SAME contexts."""
import sys, os
D = os.path.dirname(os.path.abspath(__file__))
def load(p):
    d = {}
    for l in open(p):
        f = l.rstrip('\n').split('\t')
        if len(f) >= 5: d[(f[0], f[1], f[2])] = (f[3], f[4])
    return d
M = load(os.path.join(D, 'ctx_M8.tsv'))
for g in sys.argv[1:]:
    X = load(g); c = {'SAME': 0, 'EXTRA': 0, 'NOHALT': 0, 'DIFF': 0}; dmin = None; ex = []
    for key, (res, tr) in X.items():
        if key not in M: continue
        mres, mtr = M[key]
        if not res.startswith('HALT'): c['NOHALT'] += 1; continue
        if tr == mtr:
            c['SAME'] += 1; d = int(res.split()[2]) - int(mres.split()[2]); dmin = d if dmin is None else min(dmin, d)
        elif tr.startswith(mtr.rsplit('x', 1)[0] if False else mtr) : c['EXTRA'] += 1; ex.append(tr[len(mtr):][:40])
        else: c['DIFF'] += 1
    print(os.path.basename(g), len(X), c, 'min ones delta (SAME)', dmin)
