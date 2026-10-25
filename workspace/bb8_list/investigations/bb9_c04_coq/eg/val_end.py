"""val_end.py SEED N: literal check of the endgame entry routes D0(l,s,y,P,L,t) -> Kx CL/R3 moment (my L)."""
import random, sys
sys.path.insert(0, '../tools')
from lit import *
rnd = random.Random(int(sys.argv[1])); N = int(sys.argv[2])
def far(): return '11' + ''.join(tok(rnd.randint(2, 40)) for _ in range(rnd.randint(1, 4)))[:-1]
def kx(l, toks, k, m, r, t):   # toks far->near, then k zero digits, m, r
    return l + '1' + ''.join('10' * d + '1' for d in toks) + '101' * k + '10' * m + '1' + '10' * r + '11' + T(t) + '1001'
ROUTES = {14: (lambda s, y: [s, y, 6, 7], 11, 4), 20: (lambda s, y: [s, y, 4, 9], 11, 5), 32: (lambda s, y: [s, y, 4, 5, 2, 6, 5], 20, 9)}
bad = 0
for _ in range(N):
    for L, (tk, dk, dt) in ROUTES.items():
        l = far(); s = rnd.randint(0, 30); y = rnd.randint(1, 50); P = rnd.randint(25, 140); t = rnd.randint(0, 9)
        ok, out = check(D0(l, s, y, P, L, t), kx(l, tk(s, y), P - dk, 1, 2, t + dt))
        if not ok: bad += 1; print('FAIL', L, dict(s=s, y=y, P=P, t=t), out[:80])
print('bad', bad)
