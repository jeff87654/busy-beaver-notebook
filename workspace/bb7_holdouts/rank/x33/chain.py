"""X = 1RB1RA_0RC0RA_0LD1RC_1LE1LF_1LB1LE_0LA1LG_---0LE: rule-level chain to the halt (dlscan2 rules + exhaustion rules
measured in this folder): K-config -> b1 (dlscan2 exhaustion [2,0^n,0,b1]) -> top-2 borrow [b1-2n+2, 2^(n-1)];2;1 -> b2
-> top-1 borrow [b2-2n+2, 2^(n-1)];2;1 -> b3 -> true exhaustion [b3]: HALT iff b3 odd, sigma = b3 + 3."""
import idle  # noqa
import sys
sys.path.insert(0, '..')
sys.setrecursionlimit(20000)
from rank7 import Model, Num, parse_params, trace, parse_template
X = '1RB1RA_0RC0RA_0LD1RC_1LE1LF_1LB1LE_0LA1LG_---0LE'
T = parse_template('R,A,P=110,u=1,s=0,d=1d+0,b=1b+0,S=-')
R = parse_params('R1 1b+3 | R2 a=1b+2 b=1 | R3 1b+0+0k tail=1 a=2 b=1 | R4 HKHKH')
ks, end = trace(X, T, 20000000, 400)
st, ds, a, b = ks[-1]
n = len(ds)
print('start K step %d n=%d ds=%s a=%d b=%d' % (st, n, ds, a, b))
for Q in (20160, 2 ** 10 * 9 * 5, 2 ** 7 * 27 * 25 * 7):
    M = Model(R, Q)
    b1 = M.run(ds, a, b)
    def top(bv):
        # [bv - 2n + 2, 2^(n-1)]; a=2, b=1  -> exhaustion accumulator
        d1 = M.add(bv, M.mk(0)) if False else Num(None, (bv.r - 2 * n + 2) % Q, bv.lv) if bv.huge() else M.mk(bv.ex - 2 * n + 2)
        v = M.apply(0, M.mk(2), M.mk(1))
        for j in range(1, n):
            v = M.apply(j, M.mk(2), v)
        return M.apply(n, d1, v)
    b2 = top(b1)
    b3 = top(b2)
    print('Q=%d b1 %s (odd=%d) b2 %s (odd=%d) b3 %s (odd=%d) flags=%s precond=%s' % (
        Q, b1, b1.r % 2, b2, b2.r % 2, b3, b3.r % 2, M.flags[:1], M.precond[:1]))
    print('  K_j parities', [M.K(j).r % 2 for j in range(2, 8)], ' F_j(b) parity for b=1..4 at j=1..6:',
          [[M.F(j, M.mk(bb)).r % 2 for bb in range(1, 5)] for j in range(1, 7)])
