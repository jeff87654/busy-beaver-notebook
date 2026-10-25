import sys
from lib import *
def Estar(m, j):
    return '101011011011' + '011' * m, 'E', '0' + '111' + '01' * 7 + '00' + '101' * j + '101'
m, j, N = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
L, S, R = Estar(m, j)
snaps, end = run(M10, L, S, R, N, ['snap=G0'])
prev = None; prevstep = 0
for s in snaps:
    t = tokens(s[1])
    key = tuple(t[:-3])
    if key != prev:
        print(s[0], ctok(t))
        prev = key
print('END', end[0], end[1], ctok(tokens(end[2])), '|', end[3], '|', end[4][:80])
