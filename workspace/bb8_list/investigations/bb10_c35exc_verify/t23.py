from lib import *
def Estar(m, j):
    return '101011011011' + '011' * m, 'E', '0' + '111' + '01' * 7 + '00' + '101' * j + '101'
for (k, y) in [(36, 10), (3, 10), (5, 25)]:
    snaps, end = run(R8, word([1] * k + [0, y]), 'G', '0', 10**8)
    L, S, R = Estar(2 * y + 1, k - 2)
    print(k, y, end[0], end[1])
    print('  R8 final L:', rle(end[2])[-60:], '| R:', rle(end[4])[:60])
    print('  Estar    L:', rle(L)[-60:], '| R:', rle(R)[:60])
    print('  equal:', end[2].lstrip('0') == L, end[4].rstrip('0') == R.rstrip('0'))
