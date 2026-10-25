import idle, sys
from tm import TM
m = sys.argv[1]; N = int(sys.argv[2]); every = sys.argv[3] if len(sys.argv) > 3 else 'ext'
M = TM(m); lo = hi = 0
while M.steps < N:
    if not M.step(): print('HALT', M.steps, M.halted); break
    if every == 'ext':
        if M.pos < lo or M.pos > hi:
            lo = min(lo, M.pos); hi = max(hi, M.pos)
            print(M.steps, 'L' if M.pos == lo else 'R', M.view())
