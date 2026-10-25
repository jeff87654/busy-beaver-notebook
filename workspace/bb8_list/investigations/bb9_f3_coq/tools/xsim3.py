"""X from Kt(1^n; 1; r; t): print D0 moments (D0f t L P s y l, head B on the blank right) and J/K events.
python xsim3.py n r t maxsteps"""
import sys, re
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parents[1] / 'gen'))
from tm import Sim, rle
X = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LJ0LC_0RG1LD_0LH1LH_1RI---_0RI0RF_0LK---_0RC1RH'
def D(d): return '10' * d + '1'
n, r, t, maxs = map(int, sys.argv[1:5])
w0 = '11' + D(1) * n + D(1) + '10' * r + '11' + '11111100' * t + '1001'
s = Sim(X, w0, state='B')
D0 = re.compile(r'(.*?)1((?:10)*)101((?:10)*)011((?:100)*)(1*)11((?:11111100)*)1001')
k = 0
while k < maxs:
    q, c = s.q, s.t[s.pos]
    if q in 'JK':
        print('EV step=%d %s%d' % (s.steps, q, c))
    if not s.step():
        print('HALT', s.steps); break
    k += 1
    if s.q == 'B' and s.t[s.pos] == 0 and s.t.rfind(1) < s.pos:
        w, l, rr = s.word()
        if s.pos != rr + 1: continue
        w = w[l:rr + 1]
        m = D0.fullmatch(w)
        if m:
            print('D0 step=%d t=%d L=%d P=%d s=%d y=%d far=%s' % (s.steps, len(m.group(6)) // 8, len(m.group(5)), len(m.group(4)) // 3,
                  len(m.group(2)) // 2, len(m.group(3)) // 2, rle(m.group(1))[-120:]))
        else:
            print('B step=%d %s' % (s.steps, rle(w)[:220]))
