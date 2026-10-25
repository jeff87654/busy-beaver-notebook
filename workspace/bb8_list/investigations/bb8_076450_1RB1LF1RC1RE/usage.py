"""Count how often each transition is used in the first N literal steps from the blank tape."""
import sys
from lit import Sim, ST
N = int(sys.argv[1]) if len(sys.argv) > 1 else 10**6
s = Sim()
cnt = {}
for _ in range(N):
    k = ST[s.state] + str(s.tape[s.pos])
    if not s.step():
        print('HALT', k); break
    cnt[k] = cnt.get(k, 0) + 1
for q in ST:
    for b in '01':
        print(q + b, cnt.get(q + b, 0))
