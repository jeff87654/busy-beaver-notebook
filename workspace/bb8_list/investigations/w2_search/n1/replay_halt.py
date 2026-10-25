import sys
from sim import *
for k in (2, 5):
  for n in (5, 50):
    for R in (19, 2539):
        w = far_of(k) + word_of([0] + [1]*n + [1, R]) + '1010'
        s = Sim(N1, w); r = s.run(10**8)
        wd, rel, a = s.word()
        print(k, n, R, r, s.q, s.steps, 'ones', wd.count('1'), 'head rel', rel, 'len', len(wd))
        if R == 19 and n == 5: print('   ', s.show())
