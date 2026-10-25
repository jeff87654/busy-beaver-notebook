import sys, re
from sim import *
from comp import compress
def used(j, b):
    return '101' * j + '101' + '10' * (3*b+2) + '111001'
def shape(s):
    return re.sub(r'\^\d+', '^', s)
j, b, s1 = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
thr = int(sys.argv[4]) if len(sys.argv) > 4 else 4
cfg = make(used(j, b))
step = 0
dirn = 0; sweep_start = cfg[1]
hist = []   # list of (step, comp)
while step < s1:
    p0 = cfg[1]
    snap = None
    n, h = run(cfg, 1); step += 1
    if h: print('HALT', step); break
    d = cfg[1] - p0
    if dirn != 0 and d != dirn:
        if abs(p0 - sweep_start) >= thr:
            # reconstruct previous config: undo is hard; instead record current
            hist.append((step, compress(tostr(cfg))))
        sweep_start = p0
    dirn = d
# group by shape sequence: print the first and last of each run of identical-shape snapshot cycles
prev = None
cnt = 0
for k, (st, c) in enumerate(hist):
    sh = shape(c)
    if sh != prev:
        if cnt > 1: print('   ... x%d, last %d %s' % (cnt, last[0], last[1][:200]))
        print(st, c[:200])
        prev = sh; cnt = 1
    else:
        cnt += 1
    last = (st, c)
if cnt > 1: print('   ... x%d, last %d %s' % (cnt, last[0], last[1][:200]))
