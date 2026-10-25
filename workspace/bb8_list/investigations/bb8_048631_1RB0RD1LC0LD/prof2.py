import sys
import planner9 as P
import fam9 as F
from planner9 import C
start = F.PA(C(1, z=1), C(8, y=1), C(4, x=1))
cnt = [0]
def m_log(cfg):
    q, L, R, mode = cfg
    if q == 'E' and mode == '>' and R == F.R0:
        cnt[0] += 1
        if cnt[0] > 60:
            print('EV', L[:40])
            print('   ', P.show(cfg)[-200:])
    return None
m_log.anytime = True
try:
    P.drive('RA', start, None, matchers=[m_log, F.m_TL], maxev=20000, verbose=False, maxlit=12000)
except RuntimeError as e:
    print('ERR', e)
