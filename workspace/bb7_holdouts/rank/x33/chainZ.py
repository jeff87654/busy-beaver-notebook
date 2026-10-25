"""Z = 1RB1RA_0RC0RA_0LD1RC_1LE1LF_1LB1LE_1LA1LG_---0LE (template R,B,P=10,u=1,s=0,b=3b+2): chain to the halt.
dlscan2 exhaustion [1,0^n,0,3b1+2] -> top borrow [3b1+2-2n+1, 2^(n-1)]; a=2; b=0 -> b2 -> true exhaustion [3b2+2]:
HALT iff 3b2+2 even (ones 3b2+4)."""
import idle  # noqa
import sys
sys.path.insert(0, '..')
sys.setrecursionlimit(20000)
from rank7 import Model, Num, parse_params, trace, parse_template
Zm = '1RB1RA_0RC0RA_0LD1RC_1LE1LF_1LB1LE_1LA1LG_---0LE'
T = parse_template('R,B,P=10,u=1,s=0,d=1d+0,b=3b+2,S=-')
R = parse_params('R1 1b+1 | R2 a=3b+3 b=0 | R3 3b+1+0k tail=1 a=2 b=0 | R4 HKHKH')
ks, end = trace(Zm, T, 20000000, 400)
st, ds, a, b = ks[-1]
n = len(ds)
print('start K step %d n=%d ds=%s a=%d b=%d' % (st, n, ds, a, b))
for Q in (20160, 2 ** 10 * 9 * 5, 2 ** 7 * 27 * 25 * 7):
    M = Model(R, Q)
    b1 = M.run(ds, a, b)
    d1 = Num(None, (3 * b1.r + 2 - 2 * n + 1) % Q, b1.lv)
    v = M.apply(0, M.mk(2), M.mk(0))
    for j in range(1, n):
        v = M.apply(j, M.mk(2), v)
    b2 = M.apply(n, d1, v)
    print('Q=%d b1 %s b2 %s final run 3b2+2 parity %d (0 = HALT) flags=%s' % (Q, b1, b2, (3 * b2.r + 2) % 2, M.flags[:1]))
    print('  F_j parity j=1..6, b=1..4:', [[M.F(j, M.mk(bb)).r % 2 for bb in range(1, 5)] for j in range(1, 7)])
