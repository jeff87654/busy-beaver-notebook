import idle, sys, itertools
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\reb7')
from fit7 import Prober
rows = {l.split('\t')[0]: l.strip().split('\t') for l in open(r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\reb7\grows\mach.tsv') if l.strip()}
_, m, t = rows[sys.argv[1]]
N = int(sys.argv[2]); maxlen = int(sys.argv[3]); dmax = int(sys.argv[4]); amax = int(sys.argv[5]); bmax = int(sys.argv[6])
P = Prober(m, t)
cfgs = []
for L in range(maxlen + 1):
    for ds in itertools.product(range(dmax + 1), repeat=L):
        for a in range(amax + 1):
            for b in range(0, bmax + 1):
                cfgs.append((list(ds), a, b))
res = P.probe(cfgs, N)
nh = 0
for c, r in zip(cfgs, res):
    if r[0] == 'H':
        nh += 1
        if nh <= 0: print('H', c, r)
print('total', len(cfgs), 'halts', nh, 'T', sum(1 for r in res if r[0] == 'T'))
from collections import Counter
print('halts by (a,b):', Counter((c[1], c[2]) for c, r in zip(cfgs, res) if r[0] == 'H'))
