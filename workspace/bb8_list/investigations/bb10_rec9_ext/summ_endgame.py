"""Summarise endgame.tsv: per machine one line with H(steps)/T and pair growth per probe point."""
import collections, sys
rows = collections.defaultdict(dict)
for l in open(sys.argv[1] if len(sys.argv) > 1 else 'endgame.tsv'):
    m, pt, rest = l.rstrip('\n').split('\t')
    f = rest.split()
    d = dict(x.split('=') for x in f if '=' in x)
    rows[m][pt] = (f[0], int(f[1]), int(f[4]), int(d['pairs0']), int(d['pairsmax'].split('@')[0]))
pts = sorted({p for d in rows.values() for p in d})
print('points:', pts)
for m, d in rows.items():
    cells = []
    for p in pts:
        if p not in d:
            cells.append('?'); continue
        k, st, ones, p0, pm = d[p]
        g = pm - p0
        cells.append(f'{k}{st if k == "H" else ""}' + (f'+{g}' if g > 30 else ''))
    print('_'.join(m.split('_')[8:]), ' '.join(cells))
