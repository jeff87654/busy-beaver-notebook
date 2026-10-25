import sys, collections
from machines import *
from rsim import Sim
m = globals()[sys.argv[1]]; N = int(sys.argv[2])
s = Sim(m); c = collections.Counter(); first = {}
for i in range(N):
    if s.halted: break
    sym = (s.R if s.face=='R' else s.L); sym = sym[-1][0] if sym else 0
    k = f"{s.st}{sym}"; c[k] += 1; first.setdefault(k, s.steps)
    s.step()
print(sys.argv[1], 'macro', i, 'steps', s.steps, 'halted', s.halted)
for k in sorted(c, key=lambda k: c[k]): print(f"  {k}: {c[k]}  first@{first[k]}")
