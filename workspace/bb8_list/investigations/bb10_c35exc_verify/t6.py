import lib, time
from lib import *
t = time.time()
snaps, end = run(R8, '', 'A', '', 3000000000, ['hist=G0', 'hist=E0', 'quiet'])
print('R8', end[:2], time.time() - t)
for h in lib.last_hist: print(h)
t = time.time()
snaps, end = run(M10, '', 'A', '', 3000000000, ['hist=G0', 'hist=E0', 'hist=J0', 'quiet'])
print('M10', end[:2], time.time() - t)
for h in lib.last_hist: print(h)
