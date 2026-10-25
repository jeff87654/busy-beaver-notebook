import sys
sys.path.insert(0, '.')
from evs_end import *
from probe import next_b
r = int(sys.argv[1])
S = vs(EAT_IN % (sys.argv[2], ('3 2 0 ' * r).strip()))
for j in (0, 1):
    for x in (0, 1, 2, 3):
        print(r, j, x, next_b(S, dict(K=2, j=j, x=x, A=40)))
