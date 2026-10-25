import sys
sys.argv = [sys.argv[0]] + sys.argv[1:]
import modeval9 as M
def L(b):
    m, r = divmod(b, 4)
    assert r in (0, 2)
    return [1 if r == 0 else 3] + [0, 0, 3] * m + [0, 0, 2]
for b0 in [28]:
    b1 = M.clear(L(b0), 0)
    print('b0', b0, 'b1', b1, [M.low(b1, p) for p in range(1, 12) if M.prec(b1) >= p])
