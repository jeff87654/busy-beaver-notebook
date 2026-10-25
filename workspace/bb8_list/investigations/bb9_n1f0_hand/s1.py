import sys
from c7lib import *
M = sys.argv[1]
for b in [1,2,3,4,5]:
    w = K([0]*11, 0, b)
    Path('_t.txt').write_text(J(b, 1, [1,1,1], 1, 2))
    out = tr(M, w, 1e9, 'match', '_t.txt').strip().splitlines()
    print('rebuild b=%d:' % b, out[-1] if out else '?')
for c in [0,1,2,3]:
    w = J(2, 0, [0,0,0], 0, c)
    out = tr(M, w, 2e9, 'geo', '1e30').strip().splitlines()
    print('exhaust c=%d:' % c, [x for x in out if x.startswith('HALT') or x.startswith('END')][:1], out[-1][:200])
