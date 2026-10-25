"""Print the tape at every direction change of the head (turning points), starting from a word."""
import sys
sys.path.insert(0, '..')
from tmlit import Sim, ST
TM = '1RB1RC_1LC0RE_1LF1LD_1LA1LE_1RH1RF_0LF1LG_0LD1LA_---0RA'
def run(word, off, state, maxsteps, stop=None):
    s = Sim.from_word(TM, word, off, state, size=1 << 12)
    lastdir = None
    base = s.pos - off
    prevpos = s.pos
    while s.steps < maxsteps:
        p0 = s.pos
        if not s.step():
            print('HALT'); return
        d = s.pos - p0
        if d != lastdir:
            t = ''.join(map(str, s.tape[base - 4:base + len(word) + 12]))
            hp = p0 - (base - 4)
            print('%6d %s  %s[%s]%s' % (s.steps - 1, ST[s.state], t[:hp], t[hp], t[hp+1:]))
            lastdir = d
        if stop and stop(s, base):
            break
if __name__ == '__main__':
    n, b = int(sys.argv[1]), int(sys.argv[2])
    word = '0101' * b + '11' * n + '1111' + '0' + '1' * 8
    run(word, 4 * b - 1, 'A', int(sys.argv[3]) if len(sys.argv) > 3 else 400)
