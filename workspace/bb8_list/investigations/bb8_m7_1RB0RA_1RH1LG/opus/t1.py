import sys, re
from sim import *
def used(j, b):
    return '101' * j + '101' + '10' * (3*b+2) + '111001'
def rle(s):
    # compress repeated substrings of period 1..6 appearing >= 3 times
    out = s
    return out
j, b, maxs = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
w = used(j, b)
cfg = make(w)
tape = cfg[0]
step = 0
lo_min = cfg[3] - 1
hi_max = cfg[1]
while step < maxs:
    n, h = run(cfg, 1)
    step += 1
    if h: print('HALT', step); break
    pos = cfg[1]
    if pos > hi_max:
        hi_max = pos
        print(step, 'R', tostr(cfg))
    if pos < lo_min:
        lo_min = pos
        print(step, 'L', tostr(cfg))
