import sys
import planner9 as P
import fam9 as F
from planner9 import C
start = F.PA(C(1, z=1), C(8, y=1), C(4, x=1))
# monkeypatch drive loop: wrap step to count literal steps between non-literal events
last = [None, 0]
orig_step = P.step
cnt = [0]
def step(cfg):
    cnt[0] += 1
    if cnt[0] % 2000 == 0:
        print(cnt[0], P.show(cfg)[-230:])
    return orig_step(cfg)
P.step = step
try:
    P.drive('RA', start, None, matchers=[F.m_TL], maxev=20000, verbose=False, maxlit=30000)
except RuntimeError as e:
    print('ERR', e)
