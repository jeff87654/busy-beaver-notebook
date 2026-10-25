"""Transition usage in a literal run from the blank tape: python usage.py STEPS [TM]"""
import sys
from lit import Sim, MAIN, ST
N = int(sys.argv[1]); tm = sys.argv[2] if len(sys.argv) > 2 else MAIN
s = Sim(tm, size=1 << 20)
cnt = {}
while s.steps < N:
    k = ST[s.state] + str(s.tape[s.pos])
    if not s.step():
        print('HALT at', s.steps, k); break
    cnt[k] = cnt.get(k, 0) + 1
for q in ST:
    for b in '01':
        print(q + b, cnt.get(q + b, 0))
