import sys
from sim import *
def run(M, b):
    toks = [1] * (M + 1) + [1, 3 * b + 1, 2]
    w = word(toks)
    tp = Tape(w, len(w), 'G')
    exp = [6] * (4 * b + 2) + [2, 2, 0, 5] + [1] * (M + 8 * b + 15) + [1, 1, 2]
    ew = word(exp)
    for k in range(3 * 10**7):
        if not tp.step():
            return 'HALT'
        if tp.q == 6:
            nz = [i for i, c in enumerate(tp.t) if c]
            if tp.h == nz[-1] + 1 and tp.t[tp.h - 5:tp.h] == bytearray([1, 0, 1, 0, 1]):
                s = ''.join(str(c) for c in tp.t[nz[0]:nz[-1] + 1])
                if s == ew:
                    return 'MATCH at %d' % tp.steps
    return 'nomatch'
for M, b in [(3, 1), (5, 2), (34, 1), (4, 3)]:
    print(M, b, run(M, b), flush=True)
