"""census.py: counts of holdout rows by number of undefined transitions, and how each pipeline treated rows with >= 2."""
import sys, collections, glob, os
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cnt = collections.Counter()
for f in sorted(glob.glob(os.path.join(H, 'chunks', 'c*.txt'))):
    for l in open(f):
        cnt[l.count('---')] += 1
print('list', sum(cnt.values()), dict(sorted(cnt.items())))
pf = collections.Counter(); multi = []
for f in sorted(glob.glob(os.path.join(H, 'survivors', 'c*.txt'))):
    for l in open(f):
        k = l.count('---'); pf[k] += 1
        if k >= 2: multi.append(l.strip())
print('pf7 pass', sum(pf.values()), dict(sorted(pf.items())))
open('pool_pf7_multi.txt', 'w').write('\n'.join(multi) + '\n')
s1 = collections.Counter()
for f in glob.glob(os.path.join(H, 'sample1pct', 's_*.txt')):
    for l in open(f): s1[l.count('---')] += 1
print('sample1pct inputs (dlscan2, no pf7)', dict(sorted(s1.items())))
ht = collections.Counter(); hrows = []
p = os.path.join(H, 'nonlist', 'halts.tsv')
if os.path.exists(p):
    for l in open(p):
        m = l.split('\t')[0]
        if len(m) == 48: ht[m.count('---')] += 1
        if m.count('---') >= 2: hrows.append(l.rstrip())
print('nonlist natural halts', dict(ht))
for r in hrows[:40]: print('  ', r[:160])
