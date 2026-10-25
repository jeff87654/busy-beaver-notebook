"""val_rules.py SEED N: literal check of the four sub-step rules and the stop rule on the D0 family (my L = sketch L + 1)."""
import random, sys
from lit import *
rnd = random.Random(int(sys.argv[1]) if len(sys.argv) > 1 else 1)
N = int(sys.argv[2]) if len(sys.argv) > 2 else 6
def far():
    return '11' + ''.join(tok(rnd.randint(2, 40)) for _ in range(rnd.randint(1, 4)))[:-1]
def frz(l, s, y): return l + '1' + '10' * s + '1' + '10' * y
# residue c of L = 5j + c  ->  (extra raw after freeze, s', y'(j), L'(j), dP)
SUB = {2: ('1' + '10' * 4, 5, lambda j: j - 4, lambda j: 3 * j + 8, 11),
       3: ('', 2, lambda j: j + 1, lambda j: 3 * j - 7, 4),
       4: ('', 6, lambda j: j + 2, lambda j: 3 * j - 10, 6),
       5: ('', 4, lambda j: j + 3, lambda j: 3 * j - 7, 6)}
def stop_target(l, s, y, P, j, t):
    k = j - 5   # k' = (L_sketch - 25)/5 with L_sketch = 5j
    far_ = l + '1' + '10' * s + '1' + '10' * (y + 3) + '1' + '101' * (P - 3) + tok(0) + tok(2) + '00' + tok(k + 7) + tok(1) * (k - 1)
    return far_ + tok(1) + '10' * 2 + '11' + T(t + 2) + '1001'

if __name__ == "__main__":
    ok = True
    for trial in range(N):
        for c in (1, 2, 3, 4, 5):
            l = far(); s = rnd.randint(1, 30); y = rnd.randint(1, 60); P = rnd.randint(80, 300); t = rnd.randint(0, 8)
            j = rnd.randint(12, 60)
            if c == 1: j -= j % 3; j = max(j, 15) + 0   # k' = j-5 = 0 mod 3 not required literally; test anyway
            S = D0(l, s, y, P, 5 * j + c, t)
            if c == 1:
                Tg = stop_target(l, s, y, P, j, t)
            else:
                ex, s2, yf, Lf, dP = SUB[c]
                Tg = D0(frz(l, s, y) + ex, s2, yf(j), P - dP, Lf(j), t + 3)
            r, out = check(S, Tg)
            if not r: print('FAIL c=%d' % c, dict(s=s, y=y, P=P, t=t, j=j), out[:100])
            ok &= r
    print('ALL OK' if ok else 'SOME FAIL')
    