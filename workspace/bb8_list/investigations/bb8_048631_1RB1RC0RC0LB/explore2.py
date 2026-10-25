from lit import *
from tok import tok
import sys
N = int(sys.argv[1])
st = {'lo': 0}
def cb(i, tape, pos, q):
    if pos < st['lo']:
        st['lo'] = pos
    if pos == st['lo'] and q == sys.argv[2]:
        print(i, tok(show(tape, pos, q)))
r = run(N, cb=cb)
print(r[0], r[1])
