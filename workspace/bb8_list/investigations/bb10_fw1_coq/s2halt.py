import sys
from sim import *
x, R, Z, C = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
toks = [6]*3 + [3] + [C, x, 0] + [1]*Z + [1, R, 2]
w = word(toks)
tp = Tape(w, len(w), 'G')
lo0 = tp.off - 5
for k in range(10**8):
    if not tp.step():
        print('HALT', tp.steps, 'ABCDEFGHIJ'[tp.q], tp.t[tp.h]); print(tp.show(lo0)); break
    if tp.steps > 5 * 10**7:
        print('no halt'); break
