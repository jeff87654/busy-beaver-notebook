import sys
from sim import *
from comp import compress
# print B-at-right-frontier snapshots (new max) for used(j,b)
j, b, maxs = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
cf = Cfg(used(j, b))
hi = cf.hi
while cf.steps < maxs:
    if cf.step(): print('HALT', cf.steps); break
    if cf.h > hi:
        hi = cf.h
        if cf.st == 'B':
            print(cf.steps, compress(cf.trimmed())[:250])
