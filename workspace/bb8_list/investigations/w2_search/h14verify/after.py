import sys
from sim import *
from j0look import j0
k, w, f, nb = map(int, sys.argv[1:5])
m = j0(k, w, f)
print('J0 at', m.steps)
cnt = 0; last = m.steps
while cnt < nb and m.steps < int(sys.argv[5]) if len(sys.argv)>5 else 2*10**6:
    if not m.step():
        wd, rel, a = m.word(); print('HALT', m.q, m.steps, 'rel', rel, fmt(tokens(wd[:rel])), '|', fmt(tokens(wd[rel:])) ); break
    b = bform(m)
    if b is not None:
        wd, rel, a = m.word()
        print(m.steps, m.steps-last, 'off', a, fmt(b[:-2]), '|', b[-1]); cnt += 1; last = m.steps
