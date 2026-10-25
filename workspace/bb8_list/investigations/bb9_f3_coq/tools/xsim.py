"""Literal simulation of X (or any machine) from a Kt configuration; prints Kt moments and J/K events.
python xsim.py "ds(far-first, comma)" m r t [maxsteps] [machine]"""
import sys, re
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parents[1] / 'gen'))
from tm import Sim, at_family_any, rle
X = '1RB0RA_1LC1LF_1RD0LB_1RA1LE_1LJ0LC_0RG1LD_0LH1LH_1RI---_0RI0RF_0LK---_0RC1RH'
def D(d): return '10' * d + '1'
def ktword(ds, m, r, t, fr='11'): return fr + ''.join(D(d) for d in ds) + D(m) + '10' * r + '11' + '11111100' * t + '1001'
def main():
    ds = [int(x) for x in sys.argv[1].split(',') if x]
    m, r, t = int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    maxs = int(sys.argv[5]) if len(sys.argv) > 5 else 10**7
    mach = sys.argv[6] if len(sys.argv) > 6 and sys.argv[6] != 'X' else X
    fr = sys.argv[7] if len(sys.argv) > 7 else '11'
    s = Sim(mach, ktword(ds, m, r, t, fr), state='B')
    n = 0
    while n < maxs:
        q, c = s.q, s.t[s.pos]
        if q in 'JK':
            w, l, rr = s.word()
            left = ''.join(map(str, s.t[s.pos - 3:s.pos])) 
            print('EV step=%d %s%d left3=%s' % (s.steps, q, c, left))
        if not s.step():
            print('HALT', s.steps, s.view()); return
        n += 1
        if s.q == 'B' and s.t[s.pos] == 0 and s.t.rfind(1) < s.pos and s.pos == s.word()[2] + 1 and n > 1:
            w, l, rr = s.word(); w = w[l:rr + 1]
            mm = re.fullmatch(r'(1?)((?:(?:10)*1)*?)((?:10)*)11((?:11111100)*)1001', w)
            if mm:
                ms = [len(x) // 2 for x in re.findall(r'((?:10)*)1', mm.group(2))]
                print('KT step=%d frame=%s t=%d r=%d ms=%s' % (s.steps, mm.group(1) or '-', len(mm.group(4)) // 8, len(mm.group(3)) // 2, ms if len(ms) < 40 else str(ms[:20]) + '...' + str(ms[-10:]) + ' len %d' % len(ms)))
            else:
                print('B-right step=%d %s' % (s.steps, rle(w)))
        f = None
        if f and n > 1:
            ms, rr, j = f
            print('KT step=%d t=%d r=%d ms=%s' % (s.steps, j, rr, ms if len(ms) < 40 else str(ms[:20]) + '...' + str(ms[-10:]) + ' len %d' % len(ms)))
main()
