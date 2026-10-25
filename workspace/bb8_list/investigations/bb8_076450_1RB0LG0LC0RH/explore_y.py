"""From Y(n) = 0^inf A> 0 1^n 0^inf, trace left-edge A visits (RLE) until next pure Y or halt."""
import sys
from tmlib import Sim
from rle import runs, TM

def trace(bits, maxsteps=10**7, maxprint=40):
    sim = Sim(TM, bits, pad=1 << 14)
    out = []
    while sim.steps < maxsteps:
        if not sim.step():
            out.append('HALT at %d: %s' % (sim.steps, sim.show()[:200])); return out
        if sim.state == 0 and sim.tape[sim.pos] == 0 and sim.pos <= sim.lo and sim.at_left_A0():
            w = sim.word()
            r = runs(w)
            out.append('%d %s' % (sim.steps, r[:200]))
            if ',' not in r:
                return out
    out.append('LIMIT')
    return out

if __name__ == '__main__':
    for n in range(int(sys.argv[1]), int(sys.argv[2])):
        o = trace('1' * n)
        print('Y(%d) [n mod 3 = %d]: %d visits' % (n, n % 3, len(o)))
        for l in (o if len(o) < 30 else o[:12] + ['...'] + o[-12:]):
            print('   ', l)
