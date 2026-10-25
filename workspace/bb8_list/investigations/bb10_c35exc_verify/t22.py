from lib import *
P = [2, 1, 1, 0, 2, 1, 0, 1]
bad = 0
for y in [10, 25, 40, 55, 70, 85, 100, 115, 130, 205]:
    for k in [1, 2, 3, 5, 36]:
        toks = [1] * k + [0, y]
        bf, end = bforms(M10, toks, 5 * 10**7, maxsnap=3)
        q = y // 5
        e1 = [2] + [1] * (2 * y + 4) + [0] + [1] * (k - 1) + [0, 6]
        e2 = P + [6 * q + 3] + [1] * (6 * q) + [0, 2, 7] + [1] * (k - 1) + [0, 4]
        got = [b[1] for b in bf[1:3]]
        ok = got == [e1, e2]
        if not ok:
            bad += 1
            print('y=%d k=%d' % (y, k), [ctok(g) for g in got], end[:2])
print('bad', bad)
# other residues of y mod 5 (y = 1 mod 3): what is the 2nd event?
for y in [4, 7, 13, 16, 19, 22, 28, 31]:
    toks = [1] * 3 + [0, y]
    bf, end = bforms(M10, toks, 5 * 10**7, maxsnap=3)
    print('y=%d (mod5=%d)' % (y, y % 5), [ctok(b[1]) for b in bf[1:3]], end[:2])
