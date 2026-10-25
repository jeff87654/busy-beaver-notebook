import idle, sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\reb7')
from fit7 import Prober
m, t = sys.argv[1], sys.argv[2]
N = int(sys.argv[3]) if len(sys.argv) > 3 else 30000000
cfgs = []
for ln in sys.stdin:
    f = ln.split()
    if not f: continue
    ds = [] if f[0] == '-' else [int(x) for x in f[0].split(',')]
    cfgs.append((ds, int(f[1]), int(f[2])))
P = Prober(m, t)
for c, r in zip(cfgs, P.probe(cfgs, N)):
    print(c, '->', r)
