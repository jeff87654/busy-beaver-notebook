import sys
from sim import *
x, R, Z, C = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
toks = [6]*3 + [3] + [C, x, 0] + [1]*Z + [1, R, 2]
w = word(toks)
tp = Tape(w, len(w), 'G')
for k in range(10**8):
    if not tp.step():
        nz = [i for i, c in enumerate(tp.t) if c]
        s = ''.join(str(c) for c in tp.t[nz[0]:tp.h]); r = ''.join(str(c) for c in tp.t[tp.h:nz[-1]+1])
        print('HALT', tp.steps, 'left:', s[-150:], '[I]', r[:200]); break
