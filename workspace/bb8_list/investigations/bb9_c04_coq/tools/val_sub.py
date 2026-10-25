"""val_sub.py: literal check of the sub-step rules on the D0 family."""
import random, sys
from lit import *
rnd = random.Random(int(sys.argv[1]) if len(sys.argv) > 1 else 1)
def far():
    return '11' + ''.join(tok(rnd.randint(2, 40)) for _ in range(rnd.randint(1, 4)))[:-1]   # ends inside a token
ok = True
for trial in range(12):
    l = far(); s = rnd.randint(1, 30); y = rnd.randint(1, 60); P = rnd.randint(80, 300); t = rnd.randint(0, 8); j = rnd.randint(12, 60)
    S = D0(l, s, y, P, 5 * j + 4, t)
    Tg = D0(l + '1' + '10' * s + '1' + '10' * y, 6, j + 2, P - 6, 3 * j - 10, t + 3)
    r, out = check(S, Tg)
    print('SUB3', dict(s=s, y=y, P=P, t=t, j=j), r, out[:80]); ok &= r
print('ALL OK' if ok else 'FAIL')
