"""Summarise follower results: python summ.py RESULTS.tsv [...]"""
import re, sys
from collections import Counter, defaultdict
def cls(line):
    m = re.search(r'RESULT (\S+)', line)
    r = m.group(1) if m else '?'
    fc = int(re.search(r'full_cycles=(\d+)', line).group(1)) if 'full_cycles=' in line else -1
    st = int(re.search(r'stages=(\d+)', line).group(1)) if 'stages=' in line else -1
    if r == 'HALT':
        if fc >= 2: return 'TWO-OR-MORE-REBUILDS'
        if fc == 1: return 'ONE-REBUILD'
        return 'CHAMPION-LIKE' if st == 1 else 'GROUP-1-LIKE'
    return 'UNCLEAR-' + r
tally = Counter(); ex = defaultdict(list)
for fn in sys.argv[1:]:
    for l in open(fn):
        f = l.rstrip('\n').split('\t')
        if len(f) < 3: continue
        c = cls(f[2]); tally[c] += 1; ex[c].append((f[0], f[1], f[2]))
for c, n in sorted(tally.items()): print(f'{c:24s} {n}')
for c in sorted(ex):
    if c.startswith('UNCLEAR') or c in ('ONE-REBUILD', 'TWO-OR-MORE-REBUILDS'):
        print('==', c)
        for m, tag, l in ex[c][:8]: print('  ', m, tag, l[:160])
