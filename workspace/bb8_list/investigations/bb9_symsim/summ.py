# summ.py OUTFILES... : summary of symsim R lines by holdout class (cls/*.txt) and verdict
import sys, collections, os
D = os.path.dirname(os.path.abspath(__file__))
cls = {}
for k in ('LINJ', 'NEARLINJ', 'OTHER', 'norep'):
    fn = os.path.join(D, 'cls', k + '.txt')
    if os.path.exists(fn):
        for l in open(fn): cls[tuple(l.split()[:2])] = k
T = collections.Counter(); K = collections.defaultdict(collections.Counter); rows = []
for fn in sys.argv[1:]:
    for l in open(fn):
        if not l.startswith('R '): continue
        f = l.split(); key = (f[1], f[2]); c = cls.get(key, 'broken_mid' if 'broken' in fn else '?')
        v = f[3]; det = f[4].split(':')[0] if v in ('UNDECIDED',) else f[4]
        T[(c, v)] += 1; K[c][v + ' ' + det] += 1
        if v in ('HALT', 'UNDECIDED', 'BUDGET'): rows.append(l.rstrip())
for c in sorted(K):
    print(c, sum(K[c].values()))
    for k, v in sorted(K[c].items(), key=lambda x: -x[1]): print(f'   {v:8d} {k}')
print('attention rows:', len(rows))
