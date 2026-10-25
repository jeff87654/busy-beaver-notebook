import lib
from lib import *
def Estar(m, j):
    return '101011011011' + '011' * m, 'E', '0' + '111' + '01' * 7 + '00' + '101' * j + '101'
for a in range(0, 4):
    m = 6 * a + 3
    for j in (0, 1, 2, 34):
        L, S, R = Estar(m, j)
        snaps, end = run(M10, L, S, R, 10**9, ['quiet'])
        print('a=%d m=%d j=%d' % (a, m, j), end[0], end[1])
