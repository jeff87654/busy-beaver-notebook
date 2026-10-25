"""Literal check from blank: Phi = sum of all runs (digits, a, b) mod 2 at every K event; any halt?"""
import idle  # noqa
import sys
from sim import TR
maxsteps = int(sys.argv[1])
T = bytearray(1 << 24); off = 1 << 23; p = off; q = 0; hi = -1; lo = None
nK = 0; bad = 0; last = None
for st in range(1, maxsteps + 1):
    c = T[p]; t = TR[(q, c)]
    if t is None:
        print('HALT at', st - 1); break
    T[p] = t[0]
    if t[0] and p > hi: hi = p
    p += t[1]; q = t[2]
    if q == 0 and p > hi and T[p] == 0:
        while hi >= 0 and not T[hi]: hi -= 1
        if p > hi:
            nK += 1
            ones = T.count(1)   # Phi = sum runs = number of ones
            if ones % 2: bad += 1; print('ODD PHI at step', st)
            last = (st, ones)
print('steps', maxsteps, 'K events', nK, 'odd-Phi events', bad, 'last', last)
