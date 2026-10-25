import tcycler
from lib import word, run, M10, tokens, ctok, bforms
P = [2, 1, 1, 0, 2, 1, 0, 1]
for h in (31, 61, 301):
    row = []
    for y in list(range(2, 140, 6)) + [2 * h - 10, 2 * h - 4, 2 * h + 2, 2 * h + 8, 4 * h]:
        toks = P + [44, 3, 1, 1, 0, h, 0, 1, 1, 0, 0, y]
        bf, end = bforms(M10, toks, 2 * 10**7, maxsnap=2)
        got = bf[1][1] if len(bf) > 1 else None
        exp = P + [44, 3, 1, 1, 0, h - 4, 2, 0, 2, 1, 0, 2 * y + 4]
        if got == exp: row.append('%d:ok' % y)
        elif got is None:
            tcycler.hist.clear()
            r = tcycler.check(M10, word(toks), 'G', '0', W=200, maxsteps=3 * 10**6)
            row.append('%d:%s' % (y, 'TC' if r[0] == 'TCYCLER' else 'none'))
        else: row.append('%d:other(%s)' % (y, ctok(got[12:])))
    print('h=%d' % h, ' '.join(row))
