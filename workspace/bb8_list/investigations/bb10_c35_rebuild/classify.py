"""Classify grade35 output (b = 3,4,5 per machine): REBUILD if the longest zero-digit run at a K-moment grows with b.
python classify.py GRADES.tsv [OUT.tsv]  -> one line per machine: class, maxruns, outcome at b=3, list at b=3"""
import sys, re
from collections import defaultdict, Counter
rows = defaultdict(dict)
for l in open(sys.argv[1]):
    if ' b=' not in l:
        continue
    head, _, rest = l.partition(' | ')
    f = head.split()
    m, b, out, steps, ones, ext, ne0, nk, mrun, mtok = f[0], int(f[1][2:]), f[2], int(f[3]), int(f[4]), int(f[5]), int(f[6]), int(f[7]), int(f[8]), int(f[9])
    atmax, _, last = rest.partition('|| ')
    rows[m][b] = dict(out=out, steps=steps, ones=ones, ne0=ne0, nk=nk, mrun=mrun, mtok=mtok, atmax=atmax.strip(), last=last.strip())
res = []
cnt = Counter()
for m, d in rows.items():
    if not all(b in d for b in (3, 4, 5)):
        continue
    r = [d[b]['mrun'] for b in (3, 4, 5)]
    g1, g2 = r[1] - r[0], r[2] - r[1]
    if g1 >= 2 and g2 >= 2:
        cls = 'REBUILD' if g1 == g2 else 'REBUILD?'
    elif g1 > 0 or g2 > 0:
        cls = 'GROW-SMALL'
    else:
        cls = 'FLAT'
    outs = '/'.join(d[b]['out'] for b in (3, 4, 5))
    if cls.startswith('REBUILD') and all(d[b]['out'].startswith('HALT') for b in (3, 4, 5)):
        cls += '-HALTS'
    cnt[cls] += 1
    res.append((cls, m, r, outs, d[3]['atmax']))
for k, v in cnt.most_common():
    print(f'{k:20s} {v}')
if len(sys.argv) > 2:
    with open(sys.argv[2], 'w') as f:
        for cls, m, r, outs, at in sorted(res):
            f.write(f'{cls}\t{m}\t{r}\t{outs}\t{at}\n')
