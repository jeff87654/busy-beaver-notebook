import sys
from msim import *
import asim
TM = sys.argv[1]
N = int(sys.argv[2])
m = MSim(TM)
a = asim.ASim(m)
def ev(m):
    return m.q == 'E' and m.d == 'R' and len(m.R) == 2 and m.R[-1] == [(1,0,0), 1] and m.R[0] == [(1,1,0), 1]
cnt = 0
try:
    while a.nmacro < N and cnt < int(sys.argv[3]):
        a.step()
        if ev(m):
            top = m.L[-1]
            nxt = m.L[-2] if len(m.L) > 1 else None
            if not (top[0] == (1,0,0) and nxt and nxt[0] == (1,1,1) and nxt[1] >= 2):
                print(m.steps, m.show()[:240], flush=True); cnt += 1
except Halt as h:
    print('HALT', h, m.show()[:300])
