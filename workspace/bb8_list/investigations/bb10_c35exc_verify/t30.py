from lib import *
P = [2, 1, 1, 0, 2, 1, 0, 1]
for body in ([30, 3, 1, 1, 0, 0, 13], [33, 3, 1, 1, 0, 0, 16], [12, 3, 1, 1, 0, 0, 4], [12, 3, 1, 0, 0, 4], [12, 3, 1, 1, 1, 0, 0, 4]):
    toks = P + [40] + body
    snaps, end = run(M10, word(toks), 'G', '0', 3 * 10**7, ['snap=G0', 'maxsnap=400'])
    print(body, 'snaps', len(snaps), 'end', end[0], end[1])
    for s in snaps[1:6]:
        print('   ', s[0], ctok(tokens(s[1])))
    if end[2] is not None:
        print('   final', rle(end[2])[-150:], '|', end[3], '|', rle(end[4])[:80])
