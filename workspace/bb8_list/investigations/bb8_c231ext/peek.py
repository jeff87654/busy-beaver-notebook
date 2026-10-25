import idle, sys
from tm import *
"""peek.py MACHINE a n step1,step2,... : run from K(a;0^n), print tape RLE at those steps."""
M = sys.argv[1]; a = int(sys.argv[2]); n = int(sys.argv[3]); pts = [int(x) for x in sys.argv[4].split(',')]
T, _ = parse(M)
r = Run(T, kword(a, [0] * n), 0, 4)
for s in pts:
    h = r.run(s - r.steps)
    lo, hi, L, c, R = r.view()
    print(r.steps, 'HALT' if h else '', chr(65 + r.q), '|', rle(L)[-300:], '[', c, ']', rle(R)[:300])
