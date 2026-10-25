"""Literal check of a jump + the following special, far region included (no macro): from Far(k,m) + [2, T, 1^w | A]
the literal machine must clear D(T) (T = 2 mod 3) to D2 and then do P3, reaching
[2^(k+2), 5, 1^(m-6), 0,0, A'+5, 1^w | 6] for some A' (= the clearing output).  Also CLR(9) + P2:
[2^k,5,1^m,0^3,1,P, 9, 1^(w-1) | 4] -> (CLR 9 -> D0) -> P2 output."""
import sys
from fw import *
from n1sim import literal, flab
from rules_n1 import getfar
srv_steps = 10 ** 12
for k, m, T, w, A in [(3, 20, 5, 1, 4), (5, 13, 5, 1, 7), (11, 9, 5, 1, 40), (2, 30, 5, 1, 160), (25, 7, 5, 1, 4), (40, 60, 5, 1, 520)]:
    far = getfar(k, m)
    kind, res, st, evs = literal(far, [2, T] + [1] * w, A, srv_steps)
    seq = []
    # follow literal B-forms until P3's output shape appears (far gone, list starts with 2^(k+2) 5)
    for _ in range(4000):
        if kind != 'B':
            seq.append(kind); break
        f2, L2, A2 = res
        if f2 == '' and L2[:k + 3] == [2] * (k + 2) + [5]:
            ok = L2 == [2] * (k + 2) + [5] + [1] * (m - 6) + [0, 0, L2[k + 3 + m - 6 + 2]] + [1] * w and A2 == 6
            seq.append('reached P3 output %s (A\'+5 = %d) structure_ok=%s' % (flab(f2, L2, A2)[:90], L2[k + 3 + m - 6 + 2], ok))
            break
        kind, res, st, evs = literal(f2, L2, A2, srv_steps)
    print('k=%d m=%d T=%d w=%d A=%d:' % (k, m, T, w, A), seq[-1], flush=True)
