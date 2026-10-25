"""val_top.py SEED N: TOPENTRY Kt(0,0,1^n;1;3R+2;3) -> D0('',1,6R+2,2,3n-1,4) and
TOP1 D0('',1,y,2,5j+5,t) -> D0('',0,j+3,2y+7,3j-7,t+3)."""
import random, sys
from lit import *
from ktword import build
rnd = random.Random(int(sys.argv[1])); N = int(sys.argv[2]); ok = True
for _ in range(N):
    n = rnd.randint(5, 200); R = rnd.randint(1, 60)
    r, out = check(build('0,0,1*%d;1;%d;3' % (n, 3 * R + 2)), D0('', 1, 6 * R + 2, 2, 3 * n - 1, 4))
    if not r: print('TOPENTRY FAIL', n, R, out[:100])
    ok &= r
    j = rnd.randint(5, 120); y = rnd.randint(1, 200); t = rnd.randint(0, 8)
    r, out = check(D0('', 1, y, 2, 5 * j + 5, t), D0('', 0, j + 3, 2 * y + 7, 3 * j - 7, t + 3))
    if not r: print('TOP1 FAIL', j, y, t, out[:100])
    ok &= r
print('ALL OK' if ok else 'SOME FAIL')
