"""Literal checks of R1..R4 (family K) on larger grids and of the macro decomposition."""
import itertools, sys, random
from grid1 import nxt, rule
def chk(L, a, b):
    r = rule(L, a, b)
    if r is None or r[0] == 'R4': return None
    g = nxt(L, a, b)
    return g[0] not in ('HALT', 'TIMEOUT') and (g[1], g[2], g[3]) == r
bad = tot = 0
rnd = random.Random(1)
# R3 with many zero digits, prefixes, larger digits
for k in range(0, 13):
    for b in range(0, 7):
        for y in (0, 1, 3):
            for t in ([], [0], [2], [1, 0, 2]):
                L = [0]*(k+1) + [y+1] + t
                tot += 1
                if not chk(L, 0, b): bad += 1; print('BAD R3', k, b, y, t)
# R2, R1 random
for _ in range(300):
    n = rnd.randint(1, 6)
    L = [rnd.choice([0, 1, 2, 3, 5]) for _ in range(n)]
    a = rnd.randint(0, 4); b = rnd.randint(0, 9)
    r = chk(L, a, b)
    tot += 1
    if r is False: bad += 1; print('BAD', L, a, b)
print('R1-R3 literal checks', tot, 'mismatches', bad)
# R4
from grid4 import nxt as _n
