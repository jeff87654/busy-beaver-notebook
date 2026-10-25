"""val_entry.py SEED N: exhaustion entry Kt(ctx, A, 1^P, 0,2,z2, 1^n; 1; 3R+2; t) ->* D0(ctx-1, A-3, 6R+9, P, 3n-4, t+1)."""
import random, sys
from lit import *
rnd = random.Random(int(sys.argv[1])); N = int(sys.argv[2])
ok = True
for _ in range(N):
    ctx = '11' + ''.join(tok(rnd.randint(2, 40)) for _ in range(rnd.randint(1, 4)))
    A = rnd.randint(4, 40); P = rnd.randint(60, 200); n = rnd.randint(1, 60); R = rnd.randint(0, 30); t = rnd.randint(0, 6)
    S = ctx + tok(A) + tok(1) * P + tok(0) + tok(2) + '00' + tok(1) * n + tok(1) + '10' * (3 * R + 2) + '11' + T(t) + '1001'
    Tg = D0(ctx[:-1], A - 3, 6 * R + 9, P, 3 * n - 4, t + 1)
    r, out = check(S, Tg)
    if not r: print('FAIL', dict(A=A, P=P, n=n, R=R, t=t), out[:120])
    ok &= r
print('ALL OK' if ok else 'SOME FAIL')
