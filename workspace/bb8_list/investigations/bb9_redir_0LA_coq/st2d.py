import sys, pickle, time
from common import *
from phases import *
import mexp
from planner8 import is_run
cfg = pickle.load(open('st2_p2end.pkl','rb'))
q, L, R, mode = cfg
UNIT = (1, 1, 0, 0, 1)
L3 = [('run', UNIT, (('U', 1),))] + L[1:]
P3 = (q, L3, R, mode)
pickle.dump(P3, open('st2_p3U.pkl', 'wb'))
print(pl.show(P3))
t0 = time.time()
cfg, how = drive(P3)
print(how, '%.1fs' % (time.time() - t0)); print(pl.show(cfg)[:2000])
pickle.dump(cfg, open('st2_p3Uend.pkl', 'wb'))
