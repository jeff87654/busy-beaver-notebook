# rtest.py: the I1 exhaustion of the real-class rep n = 47199400 with different accumulators R (only the parked list
# should change): R faithful mod 450000, R arbitrary (= 1 mod 5 only), R faithful mod 3150000 but larger.
import idle
from gm import run
n = 47199400
for R in (324366, 1000001, 5274366):
    r = run(f'1*{n};1;{3*R+2};6')
    print(f'R={R}:', r['kind'], r.get('state', ''), 'ones=%s' % r.get('ones'), '|', r.get('view', r.get('tape', ''))[:330], flush=True)
