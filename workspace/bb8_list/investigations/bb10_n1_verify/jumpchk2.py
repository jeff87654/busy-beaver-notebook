"""Literal jump CLR(D5 at depth 1, accumulator 4 -> D2) followed by P3, with the far region Far(k,m)."""
from fw import *
from n1sim import literal, flab
from rules_n1 import getfar
for k, m in [(11, 9), (2, 30), (25, 7), (40, 60), (7, 44)]:
    cfg = (getfar(k, m), [2, 5, 1], 4)
    for _ in range(100):
        kind, res, st, evs = literal(*cfg, 10 ** 11)
        if kind != 'B':
            print(k, m, kind); break
        f2, L2, A2 = res
        if f2 == '' and L2[:k + 3] == [2] * (k + 2) + [5]:
            ok = L2[:-2] == [2] * (k + 2) + [5] + [1] * (m - 6) + [0, 0] and L2[-1] == 1 and A2 == 6
            print('k=%d m=%d: jump+P3 literal -> %s  structure_ok=%s' % (k, m, flab(f2, L2, A2)[:100], ok), flush=True)
            break
        cfg = res
