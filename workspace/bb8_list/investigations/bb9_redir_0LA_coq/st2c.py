import sys, pickle, time
from common import *
from phases import *
import mexp
from planner8 import is_run
cfg = pickle.load(open('st2_p2end.pkl','rb'))
q, L, R, mode = cfg
UNIT = (1, 1, 0, 0, 1)
assert is_run(L[0]) and L[0][1] == UNIT * 3
L3 = [('run', UNIT * 7, (('w', 1),))] + list(UNIT) + L[1:]
P3 = (q, L3, R, mode)
pickle.dump(P3, open('st2_p3start.pkl', 'wb'))
print(pl.show(P3))
_rr = mexp.run_round
def rr(P, target, depth, maxloops=200):
    return _rr(P, target, depth, maxloops)
mexp.run_round = rr
t0 = time.time()
cfg, how = drive(P3)
print(how, '%.1fs' % (time.time() - t0)); print(pl.show(cfg)[:2000])
pickle.dump(cfg, open('st2_p3end.pkl', 'wb'))
