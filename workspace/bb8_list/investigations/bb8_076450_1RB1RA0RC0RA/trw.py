"""trace from word with head position/state: python trw.py WORD OFFSET STATE MAXSTEPS [every]"""
import sys
from fromcfg import make
from lit import ST
w, off, q, N = sys.argv[1], int(sys.argv[2]), sys.argv[3], int(sys.argv[4])
ev = int(sys.argv[5]) if len(sys.argv) > 5 else 1
filt = sys.argv[6] if len(sys.argv) > 6 else None
s = make('0' * 6 + w + '000000', 6 + off, q, size=1 << 14)
print(0, s.show(comp=False))
while s.steps < N:
    st, sym = s.state, s.tape[s.pos]
    if not s.step(): print('HALT', s.steps, s.show(comp=False)); break
    line = '%d %s%d %s' % (s.steps, ST[st], sym, s.show(comp=False))
    if (filt and (ST[s.state] + str(s.tape[s.pos])) in filt.split(',')) or (not filt and s.steps % ev == 0):
        print(line)
