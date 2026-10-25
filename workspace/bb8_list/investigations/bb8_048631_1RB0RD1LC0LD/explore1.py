import sys
from tmlit import Sim, ST
TM = sys.argv[1] if len(sys.argv) > 1 else "1RB0RD_1LC0LD_1LA1RC_0LB0RE_1LF1RA_1LG---_0LH1LE_0LA0LB"
N = int(sys.argv[2]) if len(sys.argv) > 2 else 10**6
s = Sim(TM, size=1 << 20)
from collections import Counter
usage = Counter()
s.usage = usage
while s.steps < N:
    if not s.step():
        print('HALT at', s.steps, 'ones', s.ones()); break
print(s.steps, s.ones(), s.show()[:400])
for k, v in sorted(usage.items()):
    print(ST[k[0]], k[1], v)
