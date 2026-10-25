import tcycler
from lib import word, run, M10, tokens, ctok, bforms, diff
P = [2, 1, 1, 0, 2, 1, 0, 1]
# (1) ORC rule [h, 0, 3, 0, 0, 0, y] -> [h-4, 3, 1, 1, y+1, 0, 4] for y << h and y >> h (h = 1 mod 3, y = 2 mod 6)
for h in (31, 301, 3001):
    for y in (8, 20, 98, 602, 6002):
        toks = P + [44, 3, 1, 1, 0, h - 0, 0, 3, 0, 0, 0, y]
        bf, end = bforms(M10, toks, 10**8, maxsnap=2)
        got = bf[1][1] if len(bf) > 1 else None
        exp = P + [44, 3, 1, 1, 0, h - 4, 3, 1, 1, y + 1, 0, 4]
        print('h=%d y=%d' % (h, y), 'OK' if got == exp else ('DIFF ' + (ctok(got[12:]) if got else str(end[:2]))))
# (2) runaway threshold for bigger a
for a in (300, 3000):
    for Y in (100, 2 * a + 4, 2 * a + 6, 5 * a):
        toks = P + [44, 3, 1, 1, 0, 31, 0, a, 3, 1, 1, 0, 0, Y]
        tcycler.hist.clear()
        r = tcycler.check(M10, word(toks), 'G', '0', W=150, maxsteps=3 * 10**6)
        print('a=%d Y=%d' % (a, Y), r[0])
