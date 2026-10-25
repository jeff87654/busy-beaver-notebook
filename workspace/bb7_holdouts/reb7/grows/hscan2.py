import idle, sys, itertools
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\reb7')
from fit7 import Prober
rows = {l.split('\t')[0]: l.strip().split('\t') for l in open(r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\reb7\grows\mach.tsv') if l.strip()}
_, m, t = rows[sys.argv[1]]
N = int(sys.argv[2]); maxlen = int(sys.argv[3]); digs = [int(x) for x in sys.argv[4].split(',')]; bmax = int(sys.argv[5])
P = Prober(m, t)
cfgs = [(list(ds), 0, b) for L in range(maxlen + 1) for ds in itertools.product(digs, repeat=L) for b in range(bmax + 1)]
res = P.probe(cfgs, N)
nh = 0
for c, r in zip(cfgs, res):
    if r[0] == 'H':
        nh += 1
        if nh <= 40: print('H', c, r)
print('total', len(cfgs), 'halts', nh, 'T', sum(1 for r in res if r[0] == 'T'))
