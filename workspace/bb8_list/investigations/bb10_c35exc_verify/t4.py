from lib import *
snaps, end = run(M10, '', 'A', '', 3000000, ['snap=G0'])
prev = 0
for s in snaps[:400]:
    print(s[0], s[0]-prev, rle(s[1]), '|', s[2], '|', rle(s[3]))
    prev = s[0]
