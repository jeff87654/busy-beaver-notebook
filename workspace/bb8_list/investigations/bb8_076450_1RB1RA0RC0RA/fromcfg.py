"""Simulate from a configuration: word (0/1 string), head offset (index into word, may be len), state.
Prints run-structure at right/left edge events when structure count changes."""
import sys
from lit import Sim, MAIN, ST
def make(word, off, state, tm=MAIN, size=1 << 20):
    s = Sim(tm, size=size)
    base = s.pos - off
    for i, c in enumerate(word):
        s.tape[base + i] = int(c)
    s.lo = min(base, s.pos); s.hi = max(base + len(word) - 1, s.pos)
    s.state = ST.index(state)
    return s
def desc(s):
    t = s.tape; lo, hi = s.lo, s.hi
    while lo < hi and t[lo] == 0: lo += 1
    while hi > lo and t[hi] == 0: hi -= 1
    out = []; i = lo
    while i <= hi:
        j = i
        while j <= hi and t[j] == t[i]: j += 1
        n = j - i
        if t[i] == 1: out.append(str(n))
        else: out.append('.' * n if n <= 3 else '0^%d' % n)
        i = j
    return ' '.join(out), s.pos - lo
def C(p, a, b):
    return '1' * p + '0' + '1' * a + '0' + '1' * b + '01', 'B'
if __name__ == '__main__':
    p, a, b, N = map(int, sys.argv[1:5])
    w, q = C(p, a, b)
    s = make('0' * 4 + w + '0', 4 + len(w), q)
    prevk = None
    print('start', desc(s))
    while s.steps < N:
        lo0, hi0 = s.lo, s.hi
        if not s.step():
            print('HALT at', s.steps, desc(s)); break
        if s.pos > hi0 or s.pos < lo0:
            d, pp = desc(s)
            k = d.count(' ')
            if k != prevk or 'all' in sys.argv:
                print(s.steps, ST[s.state], 'pos', pp, 'lo' if s.pos < lo0 else 'hi', ':', d)
                prevk = k
