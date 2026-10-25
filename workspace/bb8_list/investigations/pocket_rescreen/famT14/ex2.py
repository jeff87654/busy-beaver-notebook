import sys
from drv import *
from cmp import comp
# usage: ex2.py LEFT ds a b N [M]  ; LEFT is python expr using Q()
left = eval(sys.argv[1]); ds = [int(x) for x in sys.argv[2].split(',')] if sys.argv[2] != '-' else []
a, b, N = int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]); M = T2 if len(sys.argv) > 6 and sys.argv[6] == 'T2' else T1
prev = None
for L in run(left + lst(ds, a, b), N, 10**7, M):
    p = L.split(None, 2)
    if p[0] == 'E':
        c = comp(p[2]); sh = ' '.join(c.split()[:int(sys.argv[7]) if len(sys.argv) > 7 else 4])
        if sh != prev: print(p[1], c[:200])
        prev = sh
    else: print(L[:300])
