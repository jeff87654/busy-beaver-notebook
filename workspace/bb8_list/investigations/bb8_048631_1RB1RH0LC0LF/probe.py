import sys
from lit import Sim, MAIN, ST, parse
def run_from(word, state, maxsteps, stop):
    s = Sim(MAIN, 1 << 16)
    base = s.pos
    for i, ch in enumerate(word): s.tape[base + i] = int(ch)
    s.lo = base; s.hi = base + len(word) - 1
    s.pos = base + len(word); s.hi = max(s.hi, s.pos)
    s.state = ST.index(state)
    n0 = 0
    while s.steps < maxsteps:
        hi0 = s.hi
        if not s.step(): return ('HALT', s.steps, s)
        if s.pos > hi0 and ST[s.state] == 'E':
            r = stop(s)
            if r: return (r, s.steps, s)
    return ('TIMEOUT', s.steps, s)
def word(s):
    t = s.tape; lo = s.lo
    while t[lo] == 0 and lo < s.pos: lo += 1
    return ''.join(map(str, t[lo:s.pos]))
import re
if __name__ == '__main__':
    for m in range(1, 24):
        w = '10' * m
        cnt = [0]
        def stop(s):
            x = word(s)
            # stop at first E-edge whose word matches (1110)^k 11 (10)^n
            mm = re.fullmatch(r'((?:1110)*)11((?:10)*)', x)
            if mm: return 'Z(%d,%d)' % (len(mm.group(1))//4, len(mm.group(2))//2)
            return None
        r, st, s = run_from(w, 'E', 10**6, stop)
        print(m, r, st, word(s)[:80] if r != 'HALT' else s.show())
