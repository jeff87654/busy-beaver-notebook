"""E_D0 with transit << token: [P, Y, T, 0, 1^w | A], T >> 2A. outcome class per (A, T)."""
import sys
from fw import *
from hs import literal_next
P = [6, 6, 3]
Y = int(sys.argv[1]); w = int(sys.argv[2])
As = eval(sys.argv[3]); Ts = sys.argv[4]
for A in As:
    for dT in [int(x) for x in Ts.split(',')]:
        T = 2 * A + dT
        L = P + [Y, T, 0] + [1] * w
        k, L2, A2, st, evs = literal_next(L, A, 10 ** 10)
        if k == 'B':
            s = 'B [%s | %d]' % (fmt(L2), A2)
        else:
            s = 'HALT ' + show(L2)[:160]
        print('A=%d(m12=%d m8=%d) T=%d(m8=%d)' % (A, A % 12, A % 8, T, T % 8), s[:230], st, 'E0=%d' % len(evs), flush=True)
