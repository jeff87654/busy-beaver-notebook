import idle  # noqa
from sim import nxt
def run(r, maxk=100000):
    tot = 0
    for i in range(maxk):
        o = nxt(r, 10**8, size=1 << 22)
        if o[0] != 'K':
            return o[0], tot + o[1], o[2]
        tot += o[1]; r = o[2]
        if len(r) == 1: return 'EXH', tot, r
    return 'MAX', tot, r
U0 = lambda x: 3 * x + 7
def U1(x):
    v = 7
    for _ in range(x): v = U0(v)
    return v
for x in range(2, 5):
    print(x, 'model U1', U1(x), run([1, 0, 0, x]))
