"""print compressed full tapes (far-first, head marked) at moments state Q with the head within W cells of the leftmost 1"""
import idle, sys
from x3sim import *
from trace1 import comp
K, R, t, Q, W, lim = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), sys.argv[4], int(sys.argv[5]), int(sys.argv[6])
s = Sim(X3, kx_left([1] * K, 1, 3 * R + 2, t, STD))
last = -10**9
while s.steps < lim:
    if not s.step(): break
    if s.q == Q:
        lo = next(i for i in range(len(s.t)) if s.t[i])
        if s.pos - lo <= W and s.steps - last > 50:
            last = s.steps
            hi = max(i for i in range(len(s.t)) if s.t[i])
            a = comp(s.t[lo:s.pos]); b = comp(s.t[s.pos:hi + 1])
            print(s.steps, a, '[%s>]' % Q, b)
