"""Variant explorer: start at 0^inf E>0 1 (10)^a tail, run literally, print successive left-edge E0 configs
parsed as 1 (10)^a (01)^b rest (compressed)."""
import sys
from lit import Sim, compress
VAR = "1RB1LE_1RC1LE_0RD1RE_1LA---_1LG1RF_1RH0LG_1RH1LB_0RA0RG"
def parse(w):
    if not w or w[0] != 1: return None
    i = 1; a = 0
    while w[i:i+2] == [1, 0]: i += 2; a += 1
    b = 0
    while w[i:i+2] == [0, 1]: i += 2; b += 1
    return a, b, w[i:]
def run(a, tail, maxsteps, tm=VAR, maxev=10, show=True, stop_b0=True):
    s = Sim(tm, size=1 << 14)
    w = [1] + [1, 0] * a + list(tail)
    p = s.pos
    for i, x in enumerate(w): s.tape[p + 1 + i] = x
    s.hi = p + len(w); s.state = 4
    out = []
    while s.steps < maxsteps:
        lo0 = s.lo
        if not s.step():
            out.append(('HALT', s.steps, s.show())); break
        if s.state == 4 and s.tape[s.pos] == 0 and not any(s.tape[s.lo:s.pos]):
            hi = s.hi
            while hi > s.pos and s.tape[hi] == 0: hi -= 1
            ww = list(s.tape[s.pos + 1:hi + 1])
            pr = parse(ww)
            if pr and (pr[1] == 0 or not stop_b0):
                out.append((s.steps, pr[0], pr[1], compress(''.join(map(str, pr[2])))))
                if len(out) >= maxev: break
    return out
if __name__ == '__main__':
    tail = [int(c) for c in sys.argv[1]] if len(sys.argv) > 1 and sys.argv[1] != '-' else []
    for a in range(int(sys.argv[2]), int(sys.argv[3])):
        r = run(a, tail, 2 * 10**6, maxev=int(sys.argv[4]) if len(sys.argv) > 4 else 3)
        print('a=%d' % a, r)
