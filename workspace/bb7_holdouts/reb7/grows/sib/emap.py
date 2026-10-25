import idle, sys
from sibs import setup, fx
m, parent = sys.argv[1], sys.argv[2]
setup(m, parent, 'S')
lists = [[], [0], [0, 0], [1, 0, 0], [2, 0, 0], [1, 1], [2,1,1,1]] if len(sys.argv) < 4 else eval(sys.argv[3])
for ds in lists:
    out = []
    res = fx.nxt('S', [(ds, a) for a in range(0, 16)], maxs=3 * 10**8)
    for a, r in enumerate(res):
        if r[0] == 'K': out.append('%d:[%s;%d]' % (a, fx.rle(r[1]) or '-', r[2]))
        elif r[0] == 'H': out.append('%d:H' % a)
        else: out.append('%d:%s' % (a, r[0] + (str(r[2])[:30] if r[0] == 'W' else '')))
    print(fx.rle(ds) or '-', ' '.join(out))
