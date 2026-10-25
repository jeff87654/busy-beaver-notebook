import sys
from sim import *
# B-at-right-frontier snapshots (new max), raw, with the 13 tokens prefix stripped
j, b, maxs = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
cf = Cfg(used(j, b))
hi = cf.hi
pre = '101' * (j - 1)
while cf.steps < maxs:
    if cf.step(): print('HALT', cf.steps); break
    if cf.h > hi:
        hi = cf.h
        if cf.st == 'B':
            w = cf.trimmed()
            if w.startswith(pre): w = 'P ' + w[len(pre):]
            print(cf.steps, w)
