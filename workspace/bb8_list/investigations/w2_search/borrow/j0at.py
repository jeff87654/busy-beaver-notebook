"""j0at.py WORDFILE [M]: run M (default n1, J0 undefined) literally from the saved word (head right of the word, state G)
until it halts; print the tape window around the head at the halt (J0 read site) with the word's own coordinates."""
import idle  # noqa: F401  (Idle priority)

import sys
from sim import Sim, N1
w = open(sys.argv[1]).read().strip()
M = sys.argv[2] if len(sys.argv) > 2 else N1
W = int(sys.argv[3]) if len(sys.argv) > 3 else 40
s = Sim(M, w)
r = s.run(5 * 10**7)
p = s.h - s.pad
t = ''.join(map(str, s.t[s.h - W:s.h + W + 1]))
print(r, s.steps, 'state', s.q, 'pos', p, 'of word len', len(w))
print('   ' + t[:W] + '[' + t[W] + ']' + t[W + 1:])
