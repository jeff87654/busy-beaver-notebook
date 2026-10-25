import sys, time
sys.path.insert(0, '.')
from evs_end import *
import mexp
mexp.MAXLEN = 200
from planner8 import show
S, T = EVE[sys.argv[1]][:2]
depth = int(sys.argv[2])
orig = mexp.find_loop
def fl(cfg, d=1, verbose=False):
    t0 = time.time()
    r = orig(cfg, d, verbose)
    s = show(cfg)
    i = s.find('>') if '>' in s else s.find('<')
    print('find_loop d=%d %.1fs %s | %s' % (d, time.time() - t0, 'FOUND' if r else 'none', s[max(0, i - 200):i + 60]), flush=True)
    return r
mexp.find_loop = fl
t0 = time.time()
try:
    tree = mexp.explore(S, T, depth=depth, splits=4)
    print('OK', time.time() - t0)
except Exception as e:
    print('FAIL', e)
