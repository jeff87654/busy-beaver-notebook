import sys
sys.path.insert(0, '/workspace/workspace/bb_champs_17_18')
from rsim import Sim
from tm import parse

M = ('1RI0LL_1RA1RC_0LD1LG_0RE1LD_1RZ1RF_1LI0RM_1RM0LH_1LG1LH_1RN1RJ_'
     '1RE0LA_1RA0RF_1LH1LA_1RB1RM_1LO0LO_0LK1LO')

N = int(sys.argv[1]) if len(sys.argv) > 1 else 200000
every = int(sys.argv[2]) if len(sys.argv) > 2 else 20000
s = Sim(M)
for i in range(N):
    if s.halted:
        print('HALT at macrosteps', i, 'steps', s.steps)
        break
    if i % every == 0:
        def fmt(runs):
            out = []
            for sym, n in runs[-14:]:
                out.append(str(n) if sym == 1 else ('.' if n == 1 else f'.{n}.'))
            return ' '.join(out)
        print(f"{i:8d} steps={s.steps:>12} L[{fmt(s.L)}] |{s.st} {'>' if s.face=='R' else '<'}| R[{fmt(list(reversed(s.R)))}]")
    s.step()
else:
    print('after', N, 'macrosteps, steps', s.steps, 'halted', s.halted)
    print('L', s.L[:20], 'R', s.R[:20])
