"""Transition usage counts in a literal run from the blank tape."""
from lit import Sim
import sys
from collections import Counter
s = Sim(size=1 << 20)
N = int(sys.argv[1]) if len(sys.argv) > 1 else 2000000
c = Counter()
for _ in range(N):
    key = 'ABCDEFGH'[s.state] + str(s.tape[s.pos])
    if not s.step():
        print('HALT'); break
    c[key] += 1
print(N, 'steps:', ' '.join('%s:%d' % (k, c[k]) for k in sorted(c)))
missing = [q + b for q in 'ABCDEFGH' for b in '01' if c[q + b] == 0]
print('never used:', missing)
