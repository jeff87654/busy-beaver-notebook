from solve_rounds import load, classify_cell, find_period
import sys
from collections import Counter
agg = Counter()
for path in sys.argv[1:]:
    for cat, fam, tm, tab in load(path):
        kmax = max(tab)
        cls = {k: classify_cell(tab[k]) for k in range(1, kmax + 1)}
        if cls[20][0] != 'K':
            continue
        if find_period(cls, 12, kmax) is not None:
            continue
        tail = [cls[k][0] for k in range(12, kmax + 1)]
        c = Counter(tail)
        hk = [k for k in range(1, kmax + 1) if cls[k][0] == 'H']
        # dL pattern for K cells
        dls = [(k, cls[k][1]) for k in range(40, kmax + 1) if cls[k][0] == 'K'][:8]
        key = 'H>=40' if any(k >= 40 for k in hk) else 'noH>=40'
        agg[key] += 1
        print(key, fam, tm, dict(c), 'Hk=', hk[:15], 'dL40+=', dls)
print(agg)
