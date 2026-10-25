import sys
from guess3 import *
S = M3(); G = G3()
lp = engine.accelerate(S, 1)
v2 = lp['v2']
rb = lp['resultB']
print('resultB:', pl.show(rb)[:300])
tgt = engine.subst(G, 'b', ((v2,1),), 1)
print('target:', pl.show(tgt)[:300])
ops, C, how = engine.run_until_stuck(rb, pl.canon(tgt), target=tgt)
print(how, pl.show(C)[:400])
