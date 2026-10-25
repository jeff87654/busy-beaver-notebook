from msim import *
from tmlit import Sim
TM = "1RB0RD_1LC0LD_1LA1RC_0LB0RE_1LF1RA_1LG---_0LH1LE_0LA0LB"
# compare with literal: run macro sim from blank, periodically convert to binary and compare with literal at same step count
m = MSim(TM)
import itertools
def binary(m):
    Ls = ''.join(''.join(map(str, b)) * c for b, c in m.L)
    Rs = ''.join(''.join(map(str, b)) * c for b, c in reversed(m.R))
    return Ls, Rs
s = Sim(TM, size=1 << 20)
checks = 0
for it in range(20000):
    m.step()
    # advance literal to the same step count
    while s.steps < m.steps:
        s.step()
    if it % 997 == 0:
        Ls, Rs = binary(m)
        # macro head position: between L and R; literal head position depends; compare full tape strings, trimmed
        full = (Ls + Rs).strip('0')
        lo, hi = s.bounds()
        lit = ''.join(map(str, s.tape[lo:hi+1])).strip('0')
        assert full == lit, (it, m.steps)
        checks += 1
print('ok', checks, m.steps, m.show())
