"""Step trace from 0^inf F>0 <word> 0^inf (state/symbol sequence and tapes). Usage: python trace.py word nsteps [TM]"""
import sys
from lit import Sim, MAIN, ST
w = sys.argv[1]; n = int(sys.argv[2]); tm = sys.argv[3] if len(sys.argv) > 3 else MAIN
s = Sim(tm, size=4096)
for i, c in enumerate(w):
    s.tape[s.pos + 1 + i] = int(c)
s.hi = s.pos + len(w)
s.state = ST.index('F')
seq = []
for _ in range(n):
    seq.append(ST[s.state] + str(s.tape[s.pos]))
    print('%4d %s' % (s.steps, s.show(False)))
    if not s.step(): print('HALT'); break
print('%4d %s' % (s.steps, s.show(False)))
print(' '.join(seq))
