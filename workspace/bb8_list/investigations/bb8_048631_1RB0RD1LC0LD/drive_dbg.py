import sys
import planner9 as P
import fam9 as F
from planner9 import C
start = F.PA(C(1, z=1), C(8, y=1), C(4, x=1))
cnt = 0
def m_log(cfg):
    global cnt
    q, L, R, mode = cfg
    if q == 'E' and mode == '>' and R[-1] == P.BLANK and len(R) < 12:
        cnt += 1
        if 80 <= cnt < 400:
            print('EV', P.show(cfg)[-250:])
    return None
m_log.anytime = True
try:
    script, end = P.drive('RA', start, None, matchers=[m_log, F.m_TL], maxev=3000, verbose=False, maxlit=200000)
except Exception as e:
    print('EXC', e)
