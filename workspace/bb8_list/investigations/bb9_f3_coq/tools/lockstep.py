"""Lockstep check of the f3 <-> X simulation (Sim.v's Rel) from the blank tape for N f3 steps."""
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parents[1] / 'gen'))
from tm import Sim
F3 = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LH0LC_1RG1LD_0RG0RF_0LI---_0RC1RF'
X = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LJ0LC_0RG1LD_0LH1LH_1RI---_0RI0RF_0LK---_0RC1RH'
stmap = dict(zip('ABCDEFGHI', 'ABCDEFIJK'))
a = Sim(F3, '0', head=0, state='A'); b = Sim(X, '0', head=0, state='A')
def tape(s):
    w, l, r = s.word(); return (w[l:r + 1] if l >= 0 else '', s.pos - l if l >= 0 else 0)
N = int(sys.argv[1]); xs = 0; i0 = 0
for n in range(N):
    q, c = a.q, a.t[a.pos]
    alt = (b.q == 'H' and q == 'F')
    a.step()
    if q == 'F' and c == 0 and not alt:
        b.run(3); xs += 3
    else:
        b.run(1); xs += 1
    if q == 'I' and c == 0: i0 += 1
    if a.halted or b.halted: print('halt', n); break
    ok = (stmap[a.q] == b.q or (a.q == 'F' and b.q == 'H')) and a.t[a.pos] == b.t[b.pos] and (n % 200000 or tape(a) == tape(b))
    if not ok:
        print('MISMATCH at f3 step', n + 1, a.q, b.q); break
else:
    print('ok', N, 'f3 steps,', xs, 'X steps; I0 events', i0)
