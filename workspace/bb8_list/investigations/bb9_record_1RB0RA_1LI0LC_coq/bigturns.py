"""print the tokenized tape at reversals after long sweeps.  python bigturns.py WORDEXPR MAXSTEPS MINSWEEP [tail]"""
import sys
from tm import *
from tprobe import word, tail
w = eval(sys.argv[1])
mx = int(sys.argv[2])
minsw = int(sys.argv[3])
tail = sys.argv[4] if len(sys.argv) > 4 else None
s = Sim(M11, w)
lastd = 0
lastturn = s.pos
print(0, s.view())
while s.steps < mx:
    p = s.pos
    if not s.step():
        print('HALT', s.steps, s.view()); break
    d = s.pos - p
    if lastd != 0 and d != lastd:
        if abs(p - lastturn) >= minsw:
            print(s.steps, s.view())
        lastturn = p
    lastd = d
    if tail:
        f = at_family(s, tail)
        if f:
            print('FAMILY', s.steps, f, s.view()); break
