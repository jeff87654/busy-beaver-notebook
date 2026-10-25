import lib
from lib import *
def Estar(m, j):
    return '101011011011' + '011' * m, 'E', '0' + '111' + '01' * 7 + '00' + '101' * j + '101'
L, S, R = Estar(9, 3)
for n in list(range(0, 400, 10)) + [600, 800, 1000, 1200, 1290]:
    snaps, end = run(M10, L, S, R, n)
    print(n, end[0], rle(end[2]), '|', end[3], '|', rle(end[4]))
