"""successive family configs (any tail j): python tchain2.py "toks" r j NCONF MAXSTEPS"""
import sys
from tm import *
from tprobe import word, tail
toks = [int(x) for x in sys.argv[1].split(',')]
r, j, n, mx = int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
import os
MM = M12 if os.environ.get("TWIN") else M11
s = Sim(MM, word(toks, r, j))
print(0, toks, r, j)
k = 0
s.step()
while s.steps < mx and k < n:
    f = at_family_any(s)
    if f:
        print(s.steps, *f); k += 1
    if not s.step():
        print('HALT', s.steps, s.view()[:400]); break
