import sys, itertools
sys.path.insert(0, '.')
from lit1 import run, fmt
from stages import PRE6
u = 2
for P, r in [(19, 19), (2539, 19), (19, 2539)]:
    print(f'--- P={P} r={r}')
    for z in list(range(60, 76)) + [1075, 1077, 1080]:
        Q = PRE6(u, 5, 19) + [0, 3] * 7 + [0, 2, 1, 1]
        o = run(Q + [2 * P + 5, 1, 0, 1, 2] + [1] * z, 1, r)
        print(f'z={z} (z mod 5 = {z%5}, mod 4 = {z%4}): {fmt(o)}', flush=True)
