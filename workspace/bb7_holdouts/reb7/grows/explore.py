import idle, sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\reb7')
from fit7 import Prober
rows = {l.split('\t')[0]: l.strip().split('\t') for l in open(r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\reb7\grows\mach.tsv') if l.strip()}
_, m, t = rows[sys.argv[1]]
N = int(sys.argv[2]) if len(sys.argv) > 2 else 300000000
bs = [int(x) for x in sys.argv[3].split(',')] if len(sys.argv) > 3 else [1, 2, 3, 4, 5, 6, 7]
P = Prober(m, t)
groups = []
for n in range(0, 5): groups.append(('E%d' % n, [0] * n))
for k in range(0, 4): groups.append(('B1z%d' % k, [1] + [0] * k))
for k in range(0, 3): groups.append(('B2z%d' % k, [2] + [0] * k))
groups.append(('B10z1', [1, 0, 3, 0]))
for name, ds in groups:
    cfgs = [(ds, 0, b) for b in bs]
    res = P.probe(cfgs, N)
    out = []
    for b, r in zip(bs, res):
        if r[0] == 'K': out.append('b%d:%s;%d;%d' % (b, ','.join(map(str, r[1])) or '-', r[2], r[3]))
        else: out.append('b%d:%s' % (b, '/'.join(map(str, r))))
    print(name, ds, ' '.join(out), flush=True)
