import sys
import planner9 as P
import fam9 as F
from planner9 import C
start = F.PA(C(1, z=1), C(8, y=1), C(4, x=1))
tgt = F.PB(C(0,z=1), C(1,y=1), C(4029, x=27))
def m_log(cfg):
    q, L, R, mode = cfg
    if q == 'E' and mode == '>' and R == F.R0 and any(P.is_run(t) and t[2][1] == (('x', 27),) for t in L):
        print('EV', P.show(cfg))
        print('   L=', L[:30])
    return None
m_log.anytime = True
print('TGT', P.show(tgt)); print('   L=', tgt[1][:30])
P.drive('RA', start, None, matchers=[m_log, F.m_TL], maxev=20000, verbose=False, maxlit=100000)
