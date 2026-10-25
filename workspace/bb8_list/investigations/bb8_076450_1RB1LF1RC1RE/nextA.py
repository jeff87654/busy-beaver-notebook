"""Run from 0^inf [A0] word 0^inf until next left-edge A0 config (tape blank to the left of head)."""
import sys
from lit import Sim, MAIN, compress, ST

def from_word(word, tm=MAIN, maxsteps=10**7, want_left_A=True):
    s = Sim(tm, size=max(1 << 12, 8 * len(word) + 4096))
    base = s.pos
    for i, c in enumerate(word):
        s.tape[base + 1 + i] = int(c)
    s.hi = base + len(word)
    start = s.steps
    while s.steps - start < maxsteps:
        lo0 = s.lo
        if not s.step():
            return 'HALT', s
        if s.state == 0 and s.tape[s.pos] == 0 and s.pos <= s.lo and not any(s.tape[s.lo:s.pos]):
            return 'A0', s
    return 'LIMIT', s

def word_of(s):
    t = s.tape
    hi = s.hi
    while hi > s.pos and t[hi] == 0: hi -= 1
    return ''.join(map(str, t[s.pos+1:hi+1]))

if __name__ == '__main__':
    tail = sys.argv[1] if len(sys.argv) > 1 else ''
    tail = '' if tail == '-' else tail
    for n in range(1, int(sys.argv[2]) if len(sys.argv) > 2 else 20):
        w = '1' * n + tail
        r, s = from_word(w)
        print(n, n % 3, r, s.steps, compress(word_of(s)) if r == 'A0' else s.show())
