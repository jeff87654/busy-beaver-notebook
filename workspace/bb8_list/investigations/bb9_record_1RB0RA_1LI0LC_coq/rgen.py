"""rebuild from 11 D1^12 (10)^r 111001 for general r"""
import sys
from tm import *
for r in range(int(sys.argv[1]), int(sys.argv[2])):
    w = '11' + D(1) * 12 + '10' * r + '111001'
    s = Sim(M11, w)
    ok = None
    while s.steps < 3_000_000:
        if not s.step():
            print(r, 'HALT', s.steps, s.view()[:200]); break
        f = at_family(s, TAIL)
        if f:
            print(r, s.steps, f[0][:5], len(f[0]), f[0][-3:], f[1], rle(''.join(map(str, f[0][:0])))); break
    else:
        print(r, 'no family', s.view()[:300])
