"""Literal CLR(9) (depth 0, an R1-run) followed by P2, from [2^k,5,1^m,0^3,1,P,9 | 4], iterated over B-forms until the
far region appears; then compare with the P2 rule (zeros: 0 + (2P+4)/3 - 1)."""
from fw import *
from n1sim import literal, flab
from rules_n1 import getfar
for k, m, P in [(3, 20, 40), (9, 33, 1480), (25, 8, 520), (40, 60, 160)]:
    cfg = ('', [2] * k + [5] + [1] * m + [0, 0, 0, 1, P, 9], 4)
    for _ in range(50):
        kind, res, st, evs = literal(*cfg, 10 ** 11)
        if kind != 'B':
            print(k, m, P, kind); break
        if res[0]:
            f2, L2, A2 = res
            ok = f2 == getfar(k, m) and L2 == [2, 89] + [1] * ((2 * P + 4) // 3 - 1) and A2 == 4
            print('k=%d m=%d P=%d: CLR(9)+P2 literal -> %s  rule_ok=%s' % (k, m, P, flab(*res)[:100], ok), flush=True)
            break
        cfg = res
