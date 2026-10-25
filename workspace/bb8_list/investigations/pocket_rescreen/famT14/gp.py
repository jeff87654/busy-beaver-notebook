import sys
from gk import *
M, Q, z = sys.argv[1], sys.argv[2], int(sys.argv[3]); n = int(sys.argv[4]) if len(sys.argv) > 4 and sys.argv[4].isdigit() else 1
for s in sys.argv[5:] if len(sys.argv) > 4 and sys.argv[4].isdigit() else sys.argv[4:]:
    ev = gnext(M, Q, z, P(s), maxev=n)
    print('%-28s -> ' % s + ' | '.join(('z%d ' % e[2] + vshow(e[1])) if isinstance(e[0], int) and len(e) == 3 else '%s %d' % e for e in ev)[:300])
