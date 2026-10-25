import sys
import common   # Idle priority
from sim import *
M, b = int(sys.argv[1]), int(sys.argv[2])
toks = [1] * (M + 1) + [1, 3 * b + 1, 2]
w = word(toks)
tp = Tape(w, len(w), 'G')
def parse(s):
    out = []; i = 0
    while i < len(s):
        if s[i] == '1':
            j = i; m = 0
            while s[j + 1:j + 3] == '01': j += 2; m += 1
            out.append(m); i = j + 1
        else:
            out.append('_'); i += 1
    return out
def rle(v):
    o = []; i = 0
    while i < len(v):
        j = i
        while j < len(v) and v[j] == v[i]: j += 1
        o.append('%s*%d' % (v[i], j - i) if j - i > 1 else str(v[i])); i = j
    return ' '.join(o)
cnt = 0
for k in range(3 * 10**7):
    if tp.q == 5 and tp.t[tp.h] == 1:   # F reading 1
        nz = [i for i, c in enumerate(tp.t) if c]
        right = ''.join(str(c) for c in tp.t[tp.h:nz[-1] + 1])
        if right == '10101010101':
            left = ''.join(str(c) for c in tp.t[nz[0]:tp.h])
            print(tp.steps, rle(parse(left)), '| head F |', right, flush=True)
            cnt += 1
    if not tp.step():
        print('HALT'); break
    if tp.q == 6:
        nz = [i for i, c in enumerate(tp.t) if c]
        if tp.h == nz[-1] + 1 and tp.t[tp.h - 5:tp.h] == bytearray([1, 0, 1, 0, 1]) and cnt > 0:
            print('end', tp.steps, rle(parse(''.join(str(c) for c in tp.t[nz[0]:tp.h])))); break
