import sys
from kd import *
M = sys.argv[1] if len(sys.argv) > 1 and '_' in sys.argv[1] else CH10
N = int(sys.argv[-1]) if len(sys.argv) > 1 and '_' not in sys.argv[-1] else 10 ** 6
s = Sim(M)
s.usage = {}
last = 0
cnt = 0
while s.steps < N:
    u0 = dict(s.usage)
    r = run_from(s, N - s.steps)
    if r[0] != 'K':
        print(r[:3], s.show()[:300] if r[0] == 'HALT' else '')
        break
    used = sorted(ST[q] + str(c) for (q, c) in s.usage if s.usage[(q, c)] != u0.get((q, c), 0))
    ds, a, b = r[2]
    dsl = ','.join(map(str, ds)) if len(ds) < 40 else ','.join(map(str, ds[:20])) + ',...(%d)' % len(ds)
    print('step %d [+%d]: Kd [%s] %d %d  uses %s' % (r[1], r[1] - last, dsl, a, b, ''.join(used)))
    last = r[1]
