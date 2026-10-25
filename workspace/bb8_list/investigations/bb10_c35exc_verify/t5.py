from lib import *
snaps, end = run(M10, '', 'A', '', 30000000, ['snap=G0'])
prev = 0
for s in snaps:
    if s[0]-prev != 26 or True:
        print(s[0], s[0]-prev, ctok(tokens(s[1])), '|', s[2], '|', s[3])
    prev = s[0]
