from lib import *
def Estar(m, j):
    return '101011011011' + '011' * m, 'E', '0' + '111' + '01' * 7 + '00' + '101' * j + '101'
for j in (0, 1, 3, 34):
  for m in range(1, 40, 2):
    L, S, R = Estar(m, j)
    snaps, end = run(M10, L, S, R, 10**7, ['snap=G0', 'maxsnap=1'])
    if snaps:
        print('m=%d j=%d' % (m, j), snaps[0][0], ctok(tokens(snaps[0][1])))
    else:
        print('m=%d j=%d' % (m, j), 'no snap', end[0], end[1], ctok(tokens(end[2])), end[3], end[4][:60])
