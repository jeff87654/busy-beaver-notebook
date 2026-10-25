"""Variant endings: from X(a,0,1^c w) (a = 10*2^q - 6) run literally to the next phase start X(4,0,1^n w'), n >= 5.
Report n - 2a and w' for several q, to see whether the ending is uniform."""
import sys
from lit import Sim, compress
from vexp import parse, VAR
def to_phase_start(a, T, tm=VAR, maxsteps=10**7):
    s = Sim(tm, size=1 << 15)
    w = [1] + [1, 0] * a + list(T)
    p = s.pos
    for i, x in enumerate(w): s.tape[p + 1 + i] = x
    s.hi = p + len(w); s.state = 4
    while s.steps < maxsteps:
        if not s.step():
            return ('HALT', s.steps, s.show())
        if s.state == 4 and s.tape[s.pos] == 0 and not any(s.tape[s.lo:s.pos]):
            hi = s.hi
            while hi > s.pos and s.tape[hi] == 0: hi -= 1
            ww = list(s.tape[s.pos + 1:hi + 1])
            pr = parse(ww)
            if pr and pr[0] == 4 and pr[1] == 0 and pr[2][:5] == [1]*5:
                rest = pr[2]; n = 0
                while n < len(rest) and rest[n] == 1: n += 1
                return (s.steps, n, ''.join(map(str, rest[n:])))
    return ('TIMEOUT',)
def uniform(c, wstr, qs=range(1, 6)):
    T = [1]*c + [int(x) for x in wstr]
    outs = []
    for q in qs:
        a = 10 * 2**q - 6
        r = to_phase_start(a, T)
        if r[0] in ('HALT', 'TIMEOUT'):
            outs.append((q, r)); continue
        outs.append((q, r[1] - 2*a, r[2]))
    return outs
if __name__ == '__main__':
    for c in range(5):
        for w in sys.argv[1].split(','):
            w = '' if w == '-' else w
            print('c=%d w=%-10s' % (c, w), uniform(c, w))
