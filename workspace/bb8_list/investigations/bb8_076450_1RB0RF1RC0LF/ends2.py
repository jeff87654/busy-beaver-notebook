"""Level ends, followed until HALT or a level start L(p,A) = p (010)^A 0 111 01010 B>0 with A >= AMIN
(p in {1, 11}), recording intermediate Y and canonical configurations."""
import re, sys
from lit import parse, MAIN
T = parse(MAIN)
R = re.compile(r'^(.*?)((?:010)*)(01110111|0)(1+)01010$')
Y = re.compile(r'^((?:01)*)$')
AMIN = 12
def run(word, maxsteps=10**8, trace=False):
    pad = 4 * len(word) + 4096
    tape = bytearray(pad) + bytearray(int(c) for c in word) + bytearray(16 * len(word) + 16384)
    pos = pad + len(word); st = 1; steps = 0; lo = pad; hi = pad + len(word) - 1
    events = []
    while steps < maxsteps:
        e = T[st][tape[pos]]
        if e is None:
            return ('HALT', steps, events)
        wr, d, q = e
        tape[pos] = wr; pos += d; st = q; steps += 1
        if pos < lo:
            lo = pos
        if st == 0 and pos == lo and tape[pos] == 0:
            j = hi
            while tape[j] == 0: j -= 1
            s = ''.join('1' if c else '0' for c in tape[pos + 1:j + 1])
            if Y.match(s) and len(s) >= 2:
                events.append(('Y', len(s) // 2, steps))
        if pos > hi:
            hi = pos
            if st == 1:
                i = lo
                while tape[i] == 0: i += 1
                s = ''.join('1' if c else '0' for c in tape[i:pos])
                m = R.match(s)
                if m and len(m.group(1)) <= 4 and len(m.group(4)) >= 2:
                    ev = (m.group(1), len(m.group(2)) // 3, 'P' if m.group(3) == '01110111' else 'Q', len(m.group(4)), steps)
                    if ev[0] in ('1', '11') and ev[1] >= AMIN and ev[2] == 'Q' and ev[3] == 3:
                        return ('L', ev, events)
                    events.append(ev)
        if pos < 2 or pos > len(tape) - 3:
            return ('OVERFLOW', steps, events)
    return ('LIMIT', steps, events)
def word(p, kind, a, n):
    return p + '010' * a + ('01110111' if kind == 'P' else '0') + '1' * n + '01010'
if __name__ == '__main__':
    ns = [int(x) for x in sys.argv[1].split(',')] if len(sys.argv) > 1 else [31, 34, 37, 40, 43, 46, 49, 52, 55]
    for p in ('1', '11'):
        for kind, amax in (('P', 5), ('Q', 6)):
            for a in range(amax):
                for n in ns:
                    r = run(word(p, kind, a, n))
                    if r[0] == 'L':
                        print(p, kind, a, n, 'L', r[1][0], r[1][1], 'steps', r[1][4], '| via', [x[:4] for x in r[2]])
                    else:
                        print(p, kind, a, n, r[0], r[1], '| via', [x[:4] for x in r[2]])
