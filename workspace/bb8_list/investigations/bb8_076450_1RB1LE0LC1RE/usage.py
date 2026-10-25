"""Transition usage counts on the literal run from the blank tape (first N steps), with first use step."""
import sys
from lit import Sim, MAIN, ST
N = int(sys.argv[1]) if len(sys.argv) > 1 else 1000000
s = Sim(MAIN, size=1 << 20)
cnt = {}; first = {}
while s.steps < N:
    k = ST[s.state] + str(s.tape[s.pos])
    if not s.step():
        print('HALT', k, s.steps); break
    cnt[k] = cnt.get(k, 0) + 1
    first.setdefault(k, s.steps)
for q in ST:
    for b in '01':
        k = q + b
        print(k, cnt.get(k, 0), 'first at step', first.get(k))
print('distinct transitions used:', len(cnt), 'of 15 defined')
