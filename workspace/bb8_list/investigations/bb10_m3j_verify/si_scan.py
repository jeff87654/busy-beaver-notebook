"""final special S-i: [Q, 2,1,1, Y, 1,0,1, 2, 1^w | A] -> ?  scan w (and Y, A), report outcome, ones, steps."""
import sys
from fw import *
srv = Server(M10, 'Bf', 1)
Q = [9, 9, 9, 2, 7, 0, 0, 3, 3, 0, 3, 0, 3, 0, 3, 0, 2, 1, 1]
for Y, A in [(43, 40), (883, 160), (163, 1000)]:
    row = []
    for w in range(1, int(sys.argv[1])):
        L = Q[:-3] + [2, 1, 1, Y, 1, 0, 1, 2] + [1] * w
        wd, h, q = bword(L, A)
        x = srv.job(wd, h, q, 10 ** 11)[-1]
        if x['kind'] == 'HALT':
            row.append('%d:H%d' % (w, x['ones'] - (Y + A)))
        elif x['kind'] == 'BF':
            p = bparse(x['word'], x['rel'])
            row.append('%d:B' % w)
        else:
            row.append('%d:%s' % (w, x['kind'][0]))
    print('Y=%d A=%d' % (Y, A), ' '.join(row), flush=True)
srv.close()
