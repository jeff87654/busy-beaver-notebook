"""n1 endgame robustness: random k, w, P, R, F in the real class (deep values = 40 mod 120); step (1) P2 with m = 1,
step (2) after CLR(R+2 -> D0) the literal run to the halt.  Reports outcome counts and the ones formula check."""
import random, sys
from fw import *
from n1sim import literal
rng = random.Random(int(sys.argv[1])); N = int(sys.argv[2])
cnt = {}
for t in range(N):
    k = rng.randint(6, 200); w = rng.randint(1, 300)
    P = 40 + 120 * rng.randint(0, 20); R = 40 + 120 * rng.randint(0, 20); F = 40 + 120 * rng.randint(0, 40)
    kind, res, st, evs = literal('', [2] * k + [5, 1, 0, 0, 0, 1, P, 0] + [1] * w, R, 10 ** 11)
    if kind != 'B':
        key = 'P2fail:' + kind
    else:
        far2, L2, A2 = res
        w2 = len(L2) - 1
        ok1 = L2[0] == R + 2 and all(x == 1 for x in L2[1:]) and w2 == w + (2 * P + 4) // 3 - 1 and A2 == 4
        k3, r3, st3, ev3 = literal(far2, [0] + L2[1:], F, 10 ** 11)
        if k3 == 'HALT':
            key = 'P2 %s, HALT %s%d, ones-formula %s' % ('ok' if ok1 else 'BAD', r3['q'], r3['c'], r3['ones'] == 2 * w2 + F + 3 * k + 4)
        else:
            key = 'P2 %s, %s' % ('ok' if ok1 else 'BAD', k3)
    cnt[key] = cnt.get(key, 0) + 1
    print(t, k, w, P, R, F, key, flush=True)
print(cnt)
