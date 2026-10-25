"""C7 from D0f t L P s y (far l = '11' frame): run to the next D0 moment, report H0 events.  python d0test.py"""
import idle, sys, re
sys.path.insert(0, r'C:\Users\jeffr\Downloads\bb8\bb8_list\investigations\bb9_f3_coq\gen')
from tm import Sim, rle
C7 = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LH0LC_1RG1LD_0RG0RF_0LI---_1LC0RA'
D0 = re.compile(r'(.*?)1((?:10)*)101((?:10)*)011((?:100)*)(1*)11((?:11111100)*)1001')
def d0word(t, L, P, s, y, l='11'):
    return l + '1' + '10' * s + '101' + '10' * y + '011' + '100' * P + '1' * L + '11' + '11111100' * t + '1001'
def run(t, L, P, s, y, l='11', maxs=10**8, mach=C7):
    sm = Sim(mach, d0word(t, L, P, s, y, l), state='B')
    ev = []
    while sm.steps < maxs:
        if sm.q == 'H' and sm.t[sm.pos] == 0: ev.append(sm.steps)
        if not sm.step(): return ('HALT', sm.steps, ev, None)
        if sm.q == 'B' and sm.t[sm.pos] == 0 and sm.t.rfind(1) == sm.pos - 1:
            w, lo, r = sm.word(); w = w[lo:r + 1]
            m = D0.fullmatch(w)
            if m:
                return ('D0', sm.steps, ev, dict(t=len(m.group(6)) // 8, L=len(m.group(5)), P=len(m.group(4)) // 3, s=len(m.group(2)) // 2, y=len(m.group(3)) // 2, far=rle(m.group(1))[-60:]))
    return ('MAX', sm.steps, ev, rle(sm.word()[0])[-200:])
if __name__ == '__main__':
    for L in range(61, 81):
        res = run(3, L, 40, 3, 5)
        print(L, L % 5, res[0], res[1], 'H0 events', len(res[2]), res[3])
