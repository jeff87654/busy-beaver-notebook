"""cmpv.py TAG1 TAG2 ...: outcome per machine across runs (result, actual stages, deep borrows, rebuilds, last K)."""
import sys, glob, os, re, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze import one
tags = sys.argv[1:]
rows = collections.defaultdict(dict)
for t in tags:
    for p in glob.glob(f'runs/{t}_*.log'):
        m = re.search(rf'{t}_(\w{{6}}_\w{{6}})\.log$', p)
        r = one(p)
        rows[m.group(1)][t] = r
for m in sorted(rows):
    cells = []
    for t in tags:
        r = rows[m].get(t)
        if not r: cells.append('-'); continue
        res = r['res'].split()[0]
        cells.append(f"{res[:5]}/{r['ns']}/d{r['ndeep']}/L{r['looks']}")
    print(m, '\t'.join(cells))
