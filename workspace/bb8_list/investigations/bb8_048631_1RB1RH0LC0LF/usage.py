from lit import Sim, MAIN, ST
import sys
s = Sim(MAIN, 1 << 22)
cnt = {}
N = int(sys.argv[1])
while s.steps < N:
    k = (ST[s.state], s.tape[s.pos])
    cnt[k] = cnt.get(k, 0) + 1
    if not s.step(): print('halt'); break
print(sorted(cnt.items()))
