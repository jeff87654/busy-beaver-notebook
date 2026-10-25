import idle, sys
from tm import TM
# micro.py MACHINE START_STEP NSTEPS : print every step's view (window) from START_STEP
m = sys.argv[1]; S = int(sys.argv[2]); N = int(sys.argv[3]); W = int(sys.argv[4]) if len(sys.argv) > 4 else 30
M = TM(m)
while M.steps < S: M.step()
for _ in range(N):
    lo = M.pos - W; hi = M.pos + W
    _, w = M.word(lo, hi)
    c = M.t.get(M.pos, 0)
    print(M.steps, chr(65+M.q)+str(c), w[:W] + '[' + w[W] + ']' + w[W+1:])
    if not M.step(): print('HALT'); break
