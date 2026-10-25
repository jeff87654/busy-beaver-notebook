"""Trace X from Kt(1^n;1;r;t) after the first K0 event: print the view every k steps.  python xtrace.py n r t every count"""
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parents[1] / 'gen'))
from tm import Sim
X = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LJ0LC_0RG1LD_0LH1LH_1RI---_0RI0RF_0LK---_0RC1RH'
def D(d): return '10' * d + '1'
n, r, t, ev, cnt = map(int, sys.argv[1:6])
s = Sim(X, '11' + D(1) * n + D(1) + '10' * r + '11' + '11111100' * t + '1001', state='B')
while not (s.q == 'K' and s.t[s.pos] == 0): s.step()
for i in range(cnt):
    w, l, rr = s.word(); lo = min(l, s.pos) - 1; hi = max(rr, s.pos) + 1
    ww = w[lo:hi + 1]; hp = s.pos - lo
    print('%7d %s' % (s.steps, (ww[:hp] + '[' + s.q + ']' + ww[hp:])[:150]))
    for _ in range(ev): s.step()
