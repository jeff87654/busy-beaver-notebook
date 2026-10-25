import sys
from tmlit import Sim, ST
TM = sys.argv[1]
N = int(sys.argv[2])
s = Sim(TM, size=1 << 22)
cnt = 0
seen = set()
while s.steps < N:
    q, sym = s.state, s.tape[s.pos]
    if q == 3 and sym == 0:
        ctx = ''.join(map(str, s.tape[s.pos-8:s.pos])) + '[' + str(sym) + ']' + ''.join(map(str, s.tape[s.pos+1:s.pos+9]))
        # also the next few transitions
        s2 = []
        if ctx not in seen:
            seen.add(ctx)
            print(s.steps, ctx)
        cnt += 1
    if not s.step():
        print('HALT', s.steps); break
print('D0 count', cnt)
