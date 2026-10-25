"""Print run-length encoded tape at every left-edge state-A visit (literal simulation)."""
import sys
from tmlib import Sim, ST
TM = "1RB0LG_0LC0RH_---1LD_0RD1LE_1RF0LC_1RG1LG_1LA1LF_1RA1RH"

def rle(bits):
    # returns list like ['1^a','0^g',...]
    out = []
    i = 0
    while i < len(bits):
        j = i
        while j < len(bits) and bits[j] == bits[i]: j += 1
        n = j - i
        out.append((bits[i], n))
        i = j
    return out

def fmt(bits):
    r = rle(bits)
    s = []
    for b, n in r:
        if b == '1': s.append('1^%d' % n if n > 1 else '1')
        else: s.append('.' * n if n <= 3 else '0^%d' % n)
    # compress runs as run-length list
    return ' '.join(s)

def runs(bits):
    """1-run lengths separated by gap sizes: 'a|b|..' where gap>1 shown as /g/"""
    r = rle(bits)
    s = ''
    for b, n in r:
        if b == '1': s += str(n)
        else: s += ',' if n == 1 else ',%s,' % ('0' * (n - 1)).replace('0', '_')
    return s

if __name__ == '__main__':
    maxsteps = int(sys.argv[1])
    sim = Sim(TM, '', pad=1 << 16)
    last = None
    while sim.steps < maxsteps:
        if not sim.step():
            print('HALT', sim.steps, sim.show()); break
        if sim.state == 0 and sim.tape[sim.pos] == 0 and sim.pos <= sim.lo and sim.at_left_A0():
            w = sim.word()
            print(sim.steps, sim.ones(), runs(w)[:300])
