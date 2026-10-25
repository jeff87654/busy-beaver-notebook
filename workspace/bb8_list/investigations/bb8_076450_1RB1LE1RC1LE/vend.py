"""Variant: endings. Start X(a,0) = 0^inf E>0 1 (10)^a 1^c TAIL, run until the next X(4,0)-type config
(E0 at left edge, word 1 (10)^a' rest with a' small and rest starting with 1) or HALT; report."""
import sys
from lit import Sim, compress
from vexp import parse, VAR
def ending(a, c, tail, tm=VAR, maxsteps=10**6):
    s = Sim(tm, size=1 << 14)
    w = [1] + [1, 0] * a + [1] * c + list(tail)
    p = s.pos
    for i, x in enumerate(w): s.tape[p + 1 + i] = x
    s.hi = p + len(w); s.state = 4
    evs = []
    while s.steps < maxsteps:
        if not s.step():
            return ('HALT', s.steps, s.show())
        if s.state == 4 and s.tape[s.pos] == 0 and not any(s.tape[s.lo:s.pos]):
            hi = s.hi
            while hi > s.pos and s.tape[hi] == 0: hi -= 1
            ww = list(s.tape[s.pos + 1:hi + 1])
            pr = parse(ww)
            if pr and pr[1] == 0 and pr[0] >= 1:
                return (s.steps, pr[0], compress(''.join(map(str, pr[2]))))
    return ('TIMEOUT',)
if __name__ == '__main__':
    tails = sys.argv[1].split(',')
    a0, a1 = int(sys.argv[2]), int(sys.argv[3])
    for c in range(0, 5):
        for t in tails:
            tt = [] if t == '-' else [int(x) for x in t]
            res = [ending(a, c, tt) for a in range(a0, a1)]
            print('c=%d tail=%s' % (c, t))
            for a, r in zip(range(a0, a1), res):
                print('   a=%d' % a, r)
