import sys
from msim import *
import asim
TM = "1RB0RD_1LC0LD_1LA1RC_0LB0RE_1LF1RA_1LG---_0LH1LE_0LA0LB"
def ev(m):
    return m.q == 'E' and m.d == 'R' and len(m.R) == 2 and m.R[-1] == [(1,0,0), 1] and m.R[0] == [(1,1,0), 1]
def run(m, N, accel=True, allev=False):
    a = asim.ASim(m)
    while a.nmacro < N:
        if accel: a.step()
        else: m.step(); a.nmacro += 1
        if ev(m):
            top = m.L[-1]
            nxt = m.L[-2] if len(m.L) > 1 else None
            if allev or not (top[0] == (1,0,0) and nxt and nxt[0] == (1,1,1) and nxt[1] >= 2):
                print(m.steps, m.show(), flush=True)
if __name__ == '__main__':
    z, y, x = map(int, sys.argv[1:4])
    m = from_blocks(TM, [('010', z), ('000', 1), ('111', 1), ('001', y), ('000', 1), ('011', 1), ('111', 1), ('100', x+1)], 'E', 'R', [('100', 1), ('110', 1)])
    run(m, int(sys.argv[4]))
