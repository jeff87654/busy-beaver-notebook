import sys, time
from kstep import succ, show
NMAX = int(sys.argv[1]); BMAX = int(sys.argv[2]); cap = int(sys.argv[3])
for n in range(NMAX + 1):
    for b in range(BMAX + 1):
        t = time.time()
        r = succ((0,) * n, 0, b, cap)
        print('n=%d b=%d  %s   [%.1fs]' % (n, b, show(r), time.time() - t), flush=True)
