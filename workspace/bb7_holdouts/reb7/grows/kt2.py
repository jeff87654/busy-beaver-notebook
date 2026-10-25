import idle, sys
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\reb7')
from fit7 import Prober
# kt2.py ID steps maxk : K-trace printing every K (compressed: print when ds changes)
rows = {l.split('\t')[0]: l.strip().split('\t') for l in open(r'C:\Users\jeffr\Downloads\bb8\bb7_holdouts\reb7\grows\mach.tsv') if l.strip()}
_, m, t = rows[sys.argv[1]]
P = Prober(m, t)
ks, end = P.trace(int(sys.argv[2]), int(sys.argv[3]))
prev = None
for st, ds, a, b in ks:
    if ds != prev or len(sys.argv) > 4: print(st, ds, a, b)
    prev = ds
print('END', end)
