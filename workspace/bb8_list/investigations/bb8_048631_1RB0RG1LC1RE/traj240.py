"""Literal run of the mirror machine from the blank tape; check every K configuration against the rule-level successor."""
import os, sys
os.environ['BB_KENC'] = '10,0'
from kfam import run_from, set_shape, show
from tmlit import Sim
import check_rules_lib as cr
set_shape('E', '11')
TM = cr.TM
N = int(sys.argv[1]) if len(sys.argv) > 1 else 10 ** 7
s = Sim(TM, size=1 << 22)
prev = None; mism = 0; n = 0; last = 0
while s.steps < N:
    r = run_from(s, N - s.steps)
    if r[0] != 'K':
        print('ended', r[:3]); break
    cfg = r[2]
    if prev is not None:
        p = cr.predict(*prev)
        n += 1
        if p is None or p[0] != 'K' or p[1] != cfg:
            mism += 1; print('MISMATCH at step', r[1], show(prev), '->', show(cfg), 'pred', p)
    if n < 40 or n % 500 == 0:
        print('step %d: %s  (+%d)' % (r[1], show(cfg), r[1] - last))
    last = r[1]
    prev = cfg
print('configs checked', n, 'mismatches', mism, 'steps', s.steps)
