import sys
sys.path.insert(0, '.')
from collapse_test import run, P
for u in [3, 5, 8, 12]:
    Z = 2*u + 2
    for R in [19, 100, 1000, 2539, 10000, 40000]:
        print(u, Z, R, '->', run(P, u, Z, R), flush=True)
