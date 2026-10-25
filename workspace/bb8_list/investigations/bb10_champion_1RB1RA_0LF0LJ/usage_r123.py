"""Which transitions do R1, R2, R3 (grid instances) and R4 (b = 0..60) use in the BB(10) champion?"""
from kd import *
from rules import pred
import r10grade as G
M = CH10
use = {'R1': set(), 'R1e': set(), 'R2': set(), 'R3': set(), 'R4even': set(), 'R4odd': set()}
for ds, a, b in G.grid_cases():
    if a == 0 and not any(ds):
        continue
    p = pred(ds, a, b, r4=lambda x: None)
    if p is None or p[0] != 'K':
        continue
    s = kstart(M, ds, a, b)
    s.usage = {}
    r = run_from(s, 20000)
    assert r[0] == 'K' and r[2] == p[1]
    use[G.rule_kind(ds, a)] |= set(s.usage)
for b in range(61):
    s = kstart(M, (), 0, b)
    s.usage = {}
    r = run_from(s, 10 ** 6)
    use['R4odd' if b % 2 else 'R4even'] |= set(s.usage) | ({(ST.index(r[2][0]), r[2][1])} if r[0] == 'HALT' else set())
for k, v in use.items():
    print(k, ' '.join(sorted(ST[q] + str(c) for q, c in v)))
