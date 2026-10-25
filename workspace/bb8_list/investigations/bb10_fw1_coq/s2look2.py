import sys
from sim import *
N, C, x, Z, R = 1, 12, int(sys.argv[1]), 5, int(sys.argv[2])
toks = [6]*N + [3] + [C, x, 0] + [1]*Z + [1, R, 2]
w = word(toks)
tp = Tape(w, len(w), 'G')
exp = [6]*N + [3] + [C-4, 2, 0, 2*R+4-(x-3)//2] + [1]*(Z+x-2) + [1, 1, 2]
ew = word(exp)
lo0 = tp.off - 10
prevdir = 0; lasth = tp.h
for k in range(10**8):
    h0 = tp.h
    if not tp.step():
        print('HALT', tp.steps); break
    d = tp.h - h0
    if d != prevdir and prevdir != 0 and tp.steps > int(sys.argv[3]):
        # turning point
        print(tp.steps, 'ABCDEFGHIJ'[tp.q], tp.show(lo0, lo0 + 260))
    prevdir = d
    if 'ABCDEFGHIJ'[tp.q] == 'G':
        nz = [i for i, c in enumerate(tp.t) if c]
        if tp.h == nz[-1] + 1:
            s = ''.join(str(c) for c in tp.t[nz[0]:nz[-1]+1])
            if s == ew.strip('0') or s == ew:
                print('REACHED expected at', tp.steps); break
