import sys
from sim import *
N, C, x, Z, R = 1, 12, 17, 5, 19
toks = [6]*N + [3] + [C, x, 0] + [1]*Z + [1, R, 2]
w = word(toks)
tp = Tape(w, len(w), 'G')
exp = [6]*N + [3] + [C-4, 2, 0, 2*R+4-(x-3)//2] + [1]*(Z+x-2) + [1, 1, 2]
ew = word(exp)
lo0 = tp.off - 50
for k in range(10**7):
    q = 'ABCDEFGHIJ'[tp.q]
    if q in 'IJ' or (q == 'E' and tp.t[tp.h] == 0):
        print(tp.steps, tp.show(lo0, lo0 + 330))
    if not tp.step():
        print('HALT', tp.steps); break
    # check reached expected
    if 'ABCDEFGHIJ'[tp.q] == 'G':
        nz = [i for i, c in enumerate(tp.t) if c]
        if tp.h == nz[-1] + 1:
            s = ''.join(str(c) for c in tp.t[nz[0]:nz[-1]+1])
            if s == ew.strip('0') or s == ew:
                print('REACHED expected at', tp.steps); break
