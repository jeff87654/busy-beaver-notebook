"""Follow left-edge G0 configurations from a start word, printing each (compressed)."""
import sys, re
from lit import parse, MAIN, compress
from nextG import run
w = sys.argv[1]
if w.startswith('Y'):
    w = '1' * int(w[1:])
N = int(sys.argv[2]) if len(sys.argv) > 2 else 20
tot = 0
for i in range(N):
    k, st, right, mp, x = run(w)
    tot += st
    if k != 'G0':
        print('   ', k, st, x); break
    w = right
    m = re.fullmatch(r'(1*)((?:01)*)', w)
    tag = ''
    if m:
        tag = '   <== 1^%d (01)^%d' % (len(m.group(1)), len(m.group(2)) // 2)
    print('%8d %s%s' % (tot, compress(w), tag))
