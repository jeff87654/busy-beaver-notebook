"""print the tape at each direction reversal in a step window.  python turnsw.py WORDEXPR FROM TO [M12]"""
import sys
from tm import *
from tprobe import word, tail
w = eval(sys.argv[1])
a, b = int(sys.argv[2]), int(sys.argv[3])
s = Sim(M12 if len(sys.argv) > 4 else M11, w)
lastd = 0
while s.steps < b:
    p = s.pos
    if not s.step():
        print('HALT', s.steps, s.view()); break
    d = s.pos - p
    if lastd != 0 and d != lastd and s.steps >= a:
        print(s.steps, s.view())
    lastd = d
