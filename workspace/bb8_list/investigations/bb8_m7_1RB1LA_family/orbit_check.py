import sys, os
from kd import *
from grid2 import predict
from kfam import run_from
from tmlit import Sim
tm = os.environ.get('TM', TM)
N = int(sys.argv[1]) if len(sys.argv) > 1 else 3000000
s = Sim(tm)
prev = None; n = 0; bad = 0
while s.steps < N:
    r = run_from(s, N - s.steps)
    if r[0] != 'K': print(r[:3]); break
    ds, a, bu = r[2]
    assert bu % 2 == 1
    cur = (ds, a, (bu - 1) // 2)
    if prev is not None:
        p = predict(*prev)
        # the empty-list state K(;0;b) is not parsed: apply the rule once more
        if p[0] == () and p[1] == 0:
            p = predict(*p)
        if p != cur:
            bad += 1
            if bad < 5: print('MISMATCH', prev, '->', cur, 'pred', p)
    prev = cur; n += 1
print(tm, 'steps', s.steps, 'K events', n, 'mismatches', bad)
