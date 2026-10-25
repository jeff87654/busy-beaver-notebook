import time
from lib import *
t = time.time()
for i in range(50): run(M10, '', 'A', '', 100)
print('50 runs', time.time() - t)
print(run('1RB1LC_1RC1RB_1RD0LE_1LA1LD_---0LA', '', 'A', '', 10**8, ['quiet'])[1])
