"""Tabulate mini-follower histories: python an.py OUT.tsv [KIND] [MINZ]  -> machine kind nst zeros-seq last"""
import re, sys
kind = sys.argv[2] if len(sys.argv) > 2 else None
minz = int(sys.argv[3]) if len(sys.argv) > 3 else 0
rows = []
for l in open(sys.argv[1]):
    f = l.rstrip('\n').split('\t')
    if len(f) < 5: continue
    m, k, n, bj, h = f[:5]
    if kind and k != kind: continue
    zs = [int(x) for x in re.findall(r'zeros=(\d+)', h)]
    if (max(zs) if zs else 0) < minz: continue
    last = h.split(' ; ')[-1]
    rows.append((m, k, n, ' '.join(map(str, zs)), last))
for r in rows: print('\t'.join(r))
print('#', len(rows), 'rows', file=sys.stderr)
