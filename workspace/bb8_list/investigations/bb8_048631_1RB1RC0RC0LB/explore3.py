from lit import *
from tok import tok
import sys
N = int(sys.argv[1]); a = int(sys.argv[2]); b = int(sys.argv[3])
st = {'lo': 0, 'hi': 0}
def cb(i, tape, pos, q):
    ev = None
    if pos < st['lo']:
        st['lo'] = pos; ev = 'L'
    if pos > st['hi']:
        st['hi'] = pos; ev = 'R'
    if a <= i <= b and (ev or len(sys.argv) > 4):
        print(i, ev, tok(show(tape, pos, q)))
r = run(N, cb=cb)
