import sys
from lit import Sim, MAIN, ST
tm = sys.argv[2] if len(sys.argv) > 2 else MAIN
N = int(sys.argv[1])
s = Sim(tm, size=1<<20)
cnt = 0
while s.steps < N:
    if s.state == 0 and s.tape[s.pos] == 1:
        cnt += 1
        if cnt <= 12:
            p = s.pos
            ctx = ''.join(map(str, s.tape[p-6:p])) + '[' + str(s.tape[p]) + ']' + ''.join(map(str, s.tape[p+1:p+8]))
            print('A1 read at step', s.steps, 'ctx', ctx, 'dist from left edge', p - s.lo)
    if not s.step():
        print('HALT', s.steps); break
print('A1 reads:', cnt, 'in', s.steps, 'steps')
