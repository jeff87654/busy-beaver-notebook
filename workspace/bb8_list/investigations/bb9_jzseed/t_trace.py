from jzlit import *
import sys
M = CH; T = parse(M)
ds, a, b = eval(sys.argv[1])
cells = '000' + kd_cells(ds, a, b); head = 2
tp = Tape(cells, head, 3)
for n in range(int(sys.argv[2])):
    lo = min([tp.h] + list(tp.t)) ; hi = max([tp.h] + list(tp.t))
    s = ''.join(('[' if i == tp.h else '') + str(tp.get(i)) + (']' if i == tp.h else '') for i in range(min(lo, head - 2), hi + 2))
    print(n, chr(65 + tp.q), s, is_kd(tp))
    c = tp.get(tp.h); tr = T[(tp.q, c)]
    if tr is None: print('HALT'); break
    w, d, nq = tr
    if w: tp.t[tp.h] = 1
    else: tp.t.pop(tp.h, None)
    tp.h += d; tp.q = nq
