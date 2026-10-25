"""Run from X(a,0,tail) = 0^inf E>0 1 (10)^a tail 0^inf and list the following E0 left-edge configurations
(parsed as 1 (10)^a (01)^b rest) until a configuration with small a (a < a_start) and b = 0 appears."""
import sys, re
from lit import Sim, compress
M = "1RB0LA_1RC1LE_0RD1RE_1LA---_1LG1RF_1RH0LG_1RH1LB_1RA0RG"
VAR = "1RB0LA_1RC1LE_0RD1RE_1LA---_1LG1RF_0LH0LG_1RH1LB_1RA0RG"
def parse(R):
    m = re.match(r'^1((?:10)*)((?:01)*)(.*)$', R)
    return len(m.group(1)) // 2, len(m.group(2)) // 2, m.group(3)
def ending(tm, a, tail, maxsteps=10**7, verbose=False):
    s = Sim(tm, size=1 << 14)
    w = [1] + [1, 0] * a + [int(x) for x in tail]
    p = s.pos
    for i, x in enumerate(w): s.tape[p + 1 + i] = x
    s.hi = p + len(w); s.state = 4
    out = []
    while s.steps < maxsteps:
        if not s.step():
            return out + [('HALT', s.steps, s.show())]
        if s.state == 4 and s.tape[s.pos] == 0 and not any(s.tape[s.lo:s.pos]):
            hi = s.hi
            while hi > s.pos and s.tape[hi] == 0: hi -= 1
            R = ''.join(map(str, s.tape[s.pos + 1:hi + 1]))
            A, B, r = parse(R)
            if verbose: out.append((s.steps, A, B, compress(r)))
            if B == 0 and A < a and r.startswith('1') and A in (2, 3, 4, 5, 6) :
                return out + [(s.steps, A, B, compress(r), len(r))]
    return out + ['TIMEOUT']
if __name__ == '__main__':
    tm = VAR if sys.argv[1] == 'var' else M
    tails = sys.argv[2].split(',')
    As = eval(sys.argv[3])
    for t in tails:
        tt = '' if t == '-' else t
        print('tail', t)
        for a in As:
            print('  a=%d' % a, ending(tm, a, tt, verbose='-v' in sys.argv)[-1])
