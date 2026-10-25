import sys
from machines import *
from rsim import Sim
m = globals()[sys.argv[1]]; N = int(sys.argv[2]); watch = sys.argv[3]
s = Sim(m)
for i in range(N):
    if s.halted: print('HALT', s.steps); break
    if s.st in watch: print(f"{s.steps:>10} {s.tape()}")
    s.step()
