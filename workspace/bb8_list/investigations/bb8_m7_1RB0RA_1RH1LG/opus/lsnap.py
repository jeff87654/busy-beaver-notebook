import sys
from sim import *
from comp import compress
# left-frontier snapshots (new min) from a word (B at right end)
word, maxs = sys.argv[1], int(sys.argv[2])
st = sys.argv[3] if len(sys.argv) > 3 else None
cf = Cfg(word)
lo = cf.lo
while cf.steps < maxs:
    if cf.step(): print('HALT', cf.steps); break
    if cf.h < lo:
        lo = cf.h
        if st is None or cf.st == st:
            print(cf.steps, compress(cf.trimmed())[:250])
