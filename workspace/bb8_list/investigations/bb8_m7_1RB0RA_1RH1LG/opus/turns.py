import sys
from sim import *
from comp import compress
# turning points (sweep length >= thr) between steps s0 and s1, starting from a word (B at right end)
word, s0, s1 = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
thr = int(sys.argv[4]) if len(sys.argv) > 4 else 4
raw = len(sys.argv) > 5
cf = Cfg(word)
cf.step(s0)
dirn = 0; sweep_start = cf.h
prev_snap = cf.trimmed()
while cf.steps < s1:
    p0 = cf.h
    snap = cf.trimmed()
    if cf.step(): print('HALT', cf.steps); break
    d = cf.h - p0
    if dirn != 0 and d != dirn:
        if abs(p0 - sweep_start) >= thr:
            print(cf.steps - 1, snap if raw else compress(snap))
        sweep_start = p0
    dirn = d
