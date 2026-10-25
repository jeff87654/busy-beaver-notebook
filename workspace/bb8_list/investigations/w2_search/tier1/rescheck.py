"""rescheck.py MACHINE STAGES: follow from far_17+[0 1^41|1|19]; record (res mod 2520, mod) of every huge jump output."""
import sys, threading, collections
from t1lib import run, start_word, far_of
import mf35
seen = collections.Counter(); orig = mf35.rep
def rep(x, M, LB):
    if not x.exact:
        from math import gcd
        seen[(x.res % 2520 if x.mod % 2520 == 0 else ('partial', x.mod), x.mod % 2520 == 0)] += 1
    return orig(x, M, LB)
mf35.rep = rep
import fstep; fstep.mf35.rep = rep
def go():
    r = run(sys.argv[1], start_word([0] + [1] * 41 + [1, 19], far_of(17)), int(sys.argv[2]))
    print(r[0], r[1]); print(seen)
threading.stack_size(64 * 1024 * 1024); sys.setrecursionlimit(30000)
t = threading.Thread(target=go); t.start(); t.join()
