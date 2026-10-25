"""print the tokenized tape at each direction reversal.  python turns.py WORDEXPR MAXSTEPS [tail]"""
import sys
from tm import *
from tprobe import word, tail
w = eval(sys.argv[1])
mx = int(sys.argv[2])
tail = sys.argv[3] if len(sys.argv) > 3 else '111001'
s = Sim(M11, w)
lastd = 0
print(0, s.view())
while s.steps < mx:
    p = s.pos
    if not s.step():
        print('HALT', s.steps, s.view()); break
    d = s.pos - p
    if lastd != 0 and d != lastd:
        print(s.steps, s.view())
    lastd = d
    f = at_family(s, tail)
    if f:
        print('FAMILY', s.steps, f, s.view()); break
