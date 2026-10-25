"""Run literally from a canonical configuration to the next canonical one.
Canonical configs (head in state B on the blank cell right of the word, blank elsewhere):
  P(a,n) = 0^inf 1 (010)^a 0111 0111 1^n 01010 B>0 0^inf
  Q(a,n) = 0^inf 1 (010)^a 0 1^n 01010 B>0 0^inf
"""
import re, sys
from lit import parse, MAIN, ST, compress
T = parse(MAIN)
CANON = re.compile(r'^1((?:010)*)(01110111|0)(1+)01010$')

def word_P(a, n): return '1' + '010' * a + '01110111' + '1' * n + '01010'
def word_Q(a, n): return '1' + '010' * a + '0' + '1' * n + '01010'

def run_from(word, maxsteps=10**8, minn=1, want=None):
    """head in state B on cell right after word. Returns (kind, a, n, steps) at next canonical config."""
    n = len(word)
    pad = 8 * n + 4096
    tape = bytearray(pad) + bytearray(int(c) for c in word) + bytearray(8 * n + 4096)
    pos = pad + n; st = 1; steps = 0
    lo = pad; hi = pos
    tl = T
    while steps < maxsteps:
        e = tl[st][tape[pos]]
        if e is None:
            return ('HALT', None, None, steps, (tape, pos, st, lo, hi))
        w, d, q = e
        tape[pos] = w; pos += d; st = q; steps += 1
        if pos < lo:
            lo = pos
        if pos > hi:
            hi = pos
            if st == 1:
                # right edge B0 event
                i = lo
                while tape[i] == 0: i += 1
                s = tape[i:pos].decode('latin1') if False else ''.join('1' if c else '0' for c in tape[i:pos])
                m = CANON.match(s)
                if m and len(m.group(3)) >= minn:
                    kind = 'P' if m.group(2) == '01110111' else 'Q'
                    return (kind, len(m.group(1)) // 3, len(m.group(3)), steps, None)
        if pos <= 1 or pos >= len(tape) - 2:
            return ('OVERFLOW', None, None, steps, None)
    return ('LIMIT', None, None, steps, None)

if __name__ == '__main__':
    kind = sys.argv[1]; a = int(sys.argv[2]); n = int(sys.argv[3])
    w = word_P(a, n) if kind == 'P' else word_Q(a, n)
    print(run_from(w)[:4])
