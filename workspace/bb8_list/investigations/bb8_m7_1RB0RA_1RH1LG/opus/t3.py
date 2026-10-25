import sys
from sim import *
from comp import compress
def used(j, b):
    return '101' * j + '101' + '10' * (3*b+2) + '111001'
j, b, s0, s1 = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
thr = int(sys.argv[5]) if len(sys.argv) > 5 else 8
cfg = make(used(j, b))
run(cfg, s0)
step = s0
# record turning points: positions where direction changes, with sweep length >= thr
last_pos = cfg[1]; dirn = 0; sweep_start = cfg[1]
prev = None
while step < s1:
    p0 = cfg[1]
    snap = tostr(cfg)
    n, h = run(cfg, 1); step += 1
    if h: print('HALT', step); break
    d = cfg[1] - p0
    if dirn != 0 and d != dirn:
        if abs(p0 - sweep_start) >= thr:
            print(step - 1, compress(snap))
        sweep_start = p0
    if d != dirn:
        dirn = d
