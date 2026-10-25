"""Summarise a grid run: per machine, outcome per grid point (H steps / T), and grouping."""
import sys, glob, re, collections
pre = sys.argv[1]
res = collections.defaultdict(dict)
for fn in sorted(glob.glob(pre + '_*.txt')):
    q, r = map(int, re.search(r'_(\d+)_(\d+)\.txt$', fn).groups())
    for line in open(fn):
        f = line.split()
        res[f[0]][(q, r)] = (f[1], int(f[2]), f[3], f[4], int(f[5]), int(f[6]), int(f[7]))
pts = sorted(next(iter(res.values())).keys())
cls = collections.Counter()
rows = []
for m, d in res.items():
    kinds = ''.join(d[p][0] for p in pts)
    hsteps = [d[p][1] for p in pts if d[p][0] == 'H']
    tag = 'ALLH' if set(kinds) == {'H'} else 'ALLT' if set(kinds) == {'T'} else 'MIX'
    if tag == 'ALLH' and max(hsteps) < 100:
        tag = 'ALLH-QUICK'
    cls[tag] += 1
    rows.append((tag, m, kinds, max(hsteps) if hsteps else 0, ' '.join(f'{d[p][1]}' for p in pts)))
for t, c in cls.items():
    print(t, c)
for r in sorted(rows):
    if r[0] != 'ALLH-QUICK':
        print(r[0], '_'.join(r[1].split('_')[8:]), r[2], r[3])
