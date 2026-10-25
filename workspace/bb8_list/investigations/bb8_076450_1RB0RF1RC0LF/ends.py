"""Level ends: run from prefix + (010)^a + (0111 0111 | 0) + 1^n + 01010, head B on the next blank,
until HALT, a Y configuration (A>0 at the left edge followed by (01)^M then blank), or a canonical config."""
import re, sys
from lit import parse, MAIN
T = parse(MAIN)
R = re.compile(r'^(.*?)((?:010)*)(01110111|0)(1+)01010$')
Y = re.compile(r'^((?:01)*)$')
def run(word, maxsteps=10**8, state=1, headoff=None):
    pad = 4 * len(word) + 4096
    tape = bytearray(pad) + bytearray(int(c) for c in word) + bytearray(8 * len(word) + 8192)
    pos = pad + len(word) if headoff is None else pad + headoff
    st = state; steps = 0; lo = pad; hi = pad + len(word) - 1
    while steps < maxsteps:
        e = T[st][tape[pos]]
        if e is None:
            return ('HALT', steps)
        wr, d, q = e
        tape[pos] = wr; pos += d; st = q; steps += 1
        if pos < lo:
            lo = pos
        if st == 0 and pos == lo and tape[pos] == 0:
            j = hi
            while tape[j] == 0: j -= 1
            s = ''.join('1' if c else '0' for c in tape[pos + 1:j + 1])
            if Y.match(s) and len(s) >= 2:
                return ('Y', len(s) // 2, steps)
        if pos > hi:
            hi = pos
            if st == 1:
                i = lo
                while tape[i] == 0: i += 1
                s = ''.join('1' if c else '0' for c in tape[i:pos])
                m = R.match(s)
                if m and len(m.group(1)) <= 4 and len(m.group(4)) >= 2:
                    return (m.group(1), len(m.group(2)) // 3, 'P' if m.group(3) == '01110111' else 'Q', len(m.group(4)), steps)
        if pos < 2 or pos > len(tape) - 3:
            return ('OVERFLOW', steps)
    return ('LIMIT', steps)
def word(p, kind, a, n):
    return p + '010' * a + ('01110111' if kind == 'P' else '0') + '1' * n + '01010'
if __name__ == '__main__':
    for p in ('1', '11'):
        for kind, amax in (('P', 5), ('Q', 6)):
            for a in range(amax):
                for n in (31, 34, 37, 40, 43, 46):
                    print(p, kind, a, n, run(word(p, kind, a, n)))
