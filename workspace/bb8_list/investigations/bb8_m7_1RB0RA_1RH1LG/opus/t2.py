import sys
from sim import *
from comp import compress
def used(j, b):
    return '101' * j + '101' + '10' * (3*b+2) + '111001'
j, b, maxs = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
mode = sys.argv[4] if len(sys.argv) > 4 else 'LR'
cfg = make(used(j, b))
step = 0
lo_min = cfg[1] - len(used(j,b)) - 1
hi_max = cfg[1]
while step < maxs:
    n, h = run(cfg, 1)
    step += 1
    if h: print('HALT', step); break
    pos = cfg[1]
    if pos > hi_max:
        hi_max = pos
        if 'R' in mode: print(step, 'R', compress(tostr(cfg)))
    if pos < lo_min:
        lo_min = pos
        if 'L' in mode: print(step, 'L', compress(tostr(cfg)))
