import sys, time
sys.path.insert(0, '..'); import lowprio  # noqa
from cd import *
for y in sys.argv[1:]:
    t = time.time()
    r = derives([B1, parse(y)], [B2, B3], maxsize=int(__import__('os').environ.get('MS', 21)), maxkept=int(__import__('os').environ.get('MK', 1500)))
    print(y, r, round(time.time() - t, 1), flush=True)
