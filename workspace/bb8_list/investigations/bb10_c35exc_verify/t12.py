from lib import *
def Estar(m, j):
    return '101011011011' + '011' * m, 'E', '0' + '111' + '01' * 7 + '00' + '101' * j + '101'
L, S, R = Estar(21, 3)
snaps, end = run(M10, L, S, R, 3*10**6, ['snap=G0'])
prev = 0
for s in snaps[:300]:
    print(s[0], s[0]-prev, ctok(tokens(s[1])))
    prev = s[0]
